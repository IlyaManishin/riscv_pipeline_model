import pytest
from risc_v.modules.mem.dmem import DataMem
from risc_v import riscv_config as conf


def test_data_mem_initialization():
    dmem = DataMem(addr_width=6)
    
    assert dmem.get_size() == 64
    assert dmem.get_cell_size() == conf.XLEN
    
    for i in range(64):
        assert dmem.read(i) == 0
        dmem.update()
        

def test_data_mem_read_write_pipeline():
    dmem = DataMem(addr_width=4)
    
    dmem.write(addr=4, value=0xABCDEFA0)
    assert dmem.read(addr=4) == 0
    
    dmem.update()
    
    assert dmem.read(addr=4) == (0xABCDEFA0 & ((1 << conf.XLEN) - 1))


def test_data_mem_single_read_per_cycle_constraint():
    dmem = DataMem(addr_width=4)
    
    dmem.read(addr=2)
    assert dmem.read(addr=2) == 0
    
    with pytest.raises(RuntimeError, match="Memory read conflict"):
        dmem.read(addr=3)
        
    dmem.update()
    dmem.read(addr=3)


def test_data_mem_single_write_per_cycle_constraint():
    dmem = DataMem(addr_width=4)
    
    dmem.write(addr=5, value=0x1111)
    
    with pytest.raises(RuntimeError, match="Memory write conflict"):
        dmem.write(addr=5, value=0x2222)


def test_data_mem_bit_masking():
    dmem = DataMem(addr_width=4)
    mask = (1 << conf.XLEN) - 1
    
    overflow_value = mask + 42
    dmem.write(addr=1, value=overflow_value)
    dmem.update()
    
    assert dmem.read(addr=1) == (overflow_value & mask)


def test_data_mem_partial_byte_write():
    dmem = DataMem(addr_width=4)

    dmem.write(addr=0, value=0x11223344)
    dmem.update()

    dmem.write(addr=0, value=0xAABBCCDD, byte_we=0b1100)
    dmem.update()

    assert dmem.read(addr=0) == 0xAABB3344

    dmem.write(addr=0, value=0x55667788, byte_we=0b0011)
    dmem.update()

    assert dmem.read(addr=0) == 0xAABB7788


def test_data_mem_bounds_checking():
    dmem = DataMem(addr_width=4)
    size = dmem.get_size()
    
    with pytest.raises(IndexError):
        dmem.read(size)
        
    with pytest.raises(IndexError):
        dmem.write(size, 0x1)
        
    with pytest.raises(IndexError):
        dmem.read(-1)


def test_data_mem_load_data():
    dmem = DataMem(addr_width=4)
    data_block = [0xDE, 0xAD, 0xBE, 0xEF]
    
    dmem.load_data(data_block)
    
    assert dmem.read(0) == 0xDE
    dmem.update()
    assert dmem.read(3) == 0xEF


def test_data_mem_load_data_overflow():
    dmem = DataMem(addr_width=2)
    big_data_block = [1, 2, 3, 4, 5]
    
    with pytest.raises(ValueError, match="exceeds the amount of data memory"):
        dmem.load_data(big_data_block)


def test_data_mem_invalid_byte_we():
    dmem = DataMem(addr_width=4)
    
    with pytest.raises(ValueError, match="out of range"):
        dmem.write(addr=0, value=0x11, byte_we=0xFF)