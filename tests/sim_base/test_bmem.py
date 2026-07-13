import pytest
from sim_base.mem.block_mem import BlockMem


def test_block_mem_value_without_overflow():
    bmem = BlockMem(addr_width=4, cell_size=16)
    
    bmem.write(addr=5, value=0x1234)
    bmem.update()
    
    assert bmem.read(addr=5) == 0x1234


def test_block_mem_value_with_overflow():
    bmem = BlockMem(addr_width=4, cell_size=16)
    
    bmem.write(addr=5, value=0x9ABCDEF)
    bmem.update()
    
    assert bmem.read(addr=5) == 0xCDEF


def test_block_mem_address_without_overflow_valid():
    bmem = BlockMem(addr_width=4, cell_size=16, addr_overflow=False)
    
    bmem.write(addr=15, value=0xAAAA)
    bmem.update()
    
    assert bmem.read(addr=15) == 0xAAAA


def test_block_mem_address_without_overflow_invalid():
    bmem = BlockMem(addr_width=4, cell_size=16, addr_overflow=False)
    
    with pytest.raises(IndexError):
        bmem.write(addr=16, value=0x1111)
        
    with pytest.raises(IndexError):
        bmem.read(addr=16)


def test_block_mem_address_with_overflow():
    bmem = BlockMem(addr_width=4, cell_size=16, addr_overflow=True)
    
    bmem.write(addr=18, value=0xBBBB)
    bmem.update()
    
    assert bmem.read(addr=2) == 0xBBBB
    assert bmem.read(addr=18) == 0xBBBB


def test_block_mem_partial_byte_write_with_value_overflow():
    bmem = BlockMem(addr_width=4, cell_size=16)
    
    bmem.write(addr=0, value=0x1122)
    bmem.update()
    
    bmem.write(addr=0, value=0x9999FF55, byte_we=0b01)
    bmem.update()
    
    assert bmem.read(addr=0) == 0x1155