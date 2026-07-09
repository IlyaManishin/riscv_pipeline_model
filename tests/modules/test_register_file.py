import pytest

from risc_v.modules.mem.reg_file import RegFile


def test_register_file_initialization():
    rf = RegFile()
    assert rf.get_size() == 32
    assert rf.get_cell_size() == 32
    for i in range(32):
        assert rf.read(i) == 0

def test_register_file_read_write_cycle():
    rf = RegFile()
    
    rf.write(address=1, value=42)
    assert rf.read(1) == 0
    
    rf.update()
    assert rf.read(1) == 42

def test_register_file_x0_always_zero():
    rf = RegFile()
    
    rf.write(address=0, value=100)
    rf.update()
    
    assert rf.read(0) == 0

def test_register_file_bit_masking():
    rf = RegFile()
    
    rf.write(address=5, value=0xFFFFFFFF + 5)
    rf.update()
    
    assert rf.read(5) == 4

def test_register_file_multiple_writes_conflict():
    rf = RegFile()
    rf.write(address=2, value=10)
    
    with pytest.raises(RuntimeError, match="Memory write conflict"):
        rf.write(address=3, value=20)

def test_register_file_bounds_checking():
    rf = RegFile()
    
    with pytest.raises(IndexError):
        rf.read(32)
        
    with pytest.raises(IndexError):
        rf.write(32, 10)
        rf.update()