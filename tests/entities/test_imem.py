import pytest
from src.riscv_entities.memory.imem import InstrMem

def test_imem_load_and_async_read_cycle():
    imem = InstrMem(size=16)
    program = [0x00100093, 0x00200113, 0x002081b3]
    imem.load_program(program)

    assert imem.read(0) == 0x00100093

    with pytest.raises(RuntimeError, match="Memory read conflict"):
        imem.read(0)

    imem.update()

    assert imem.read(1) == 0x00200113

def test_imem_write_protection():
    imem = InstrMem(size=16)
    
    with pytest.raises(PermissionError, match="read-only"):
        imem.write(address=0, value=0x00100093)

def test_imem_load_overflow():
    imem = InstrMem(size=2)
    big_program = [1, 2, 3]
    
    with pytest.raises(ValueError, match="exceeds Instruction Memory capacity"):
        imem.load_program(big_program)