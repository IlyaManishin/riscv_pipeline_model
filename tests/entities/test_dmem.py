import pytest

from risc_v.entities.mem.dmem import DataMem
from risc_v import riscv_config as conf

def test_data_mem_initialization():
    size = 64
    dmem = DataMem(size=size)
    
    assert dmem.size == size
    assert dmem.cell_size == conf.XLEN
    
    for i in range(size):
        assert dmem.read(i) == 0
        dmem.update()
        

def test_data_mem_read_write_pipeline():
    dmem = DataMem(size=16)
    
    dmem.write(address=4, value=0xABCDEFA0)
    assert dmem.read(address=4) == 0
    
    dmem.update()
    
    assert dmem.read(address=4) == (0xABCDEFA0 & ((1 << conf.XLEN) - 1))

def test_data_mem_single_read_per_cycle_constraint():
    dmem = DataMem(size=16)
    
    dmem.read(address=2)
    
    with pytest.raises(RuntimeError, match="Memory read conflict"):
        dmem.read(address=2)
        
    dmem.update()
    dmem.read(address=2)

def test_data_mem_single_write_per_cycle_constraint():
    dmem = DataMem(size=16)
    
    dmem.write(address=5, value=0x1111)
    
    with pytest.raises(RuntimeError, match="Memory write conflict"):
        dmem.write(address=5, value=0x2222)

def test_data_mem_bit_masking():
    dmem = DataMem(size=16)
    mask = (1 << conf.XLEN) - 1
    
    overflow_value = mask + 42
    dmem.write(address=1, value=overflow_value)
    dmem.update()
    
    assert dmem.read(address=1) == (overflow_value & mask)

def test_data_mem_bounds_checking():
    size = 10
    dmem = DataMem(size=size)
    
    with pytest.raises(IndexError):
        dmem.read(size)
        
    with pytest.raises(IndexError):
        dmem.write(size, 0x1)
        
    with pytest.raises(IndexError):
        dmem.read(-1)