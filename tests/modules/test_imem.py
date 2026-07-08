import pytest

from risc_v.modules.mem.imem import InstrMem


def test_imem_load_and_sync_read_cycle():
    imem = InstrMem(addr_width=4)
    program = [0x00100093, 0x00200113, 0x002081b3]
    imem.load_program(program)

    assert imem.read(0) == 0x00100093
    assert imem.read(0) == 0x00100093

    with pytest.raises(RuntimeError, match="Memory read conflict"):
        imem.read(1)

    imem.update()
    assert imem.read(1) == 0x00200113


def test_imem_write_protection():
    imem = InstrMem(addr_width=4)

    with pytest.raises(PermissionError, match="read-only"):
        imem.write(addr=0, value=0x00100093)


def test_imem_load_overflow():
    imem = InstrMem(addr_width=1)
    big_program = [1, 2, 3]

    with pytest.raises(ValueError, match="exceeds Instruction Memory capacity"):
        imem.load_program(big_program)


def test_imem_read_out_of_bounds():
    imem = InstrMem(addr_width=2)

    with pytest.raises(IndexError, match="out of memory bounds"):
        imem.read(4)


def test_imem_load_program_masking():
    imem = InstrMem(addr_width=2, cell_size=8)
    program = [0x1FF]
    imem.load_program(program)

    assert imem.read(0) == 0xFF


def test_imem_initial_state_is_zero():
    imem = InstrMem(addr_width=2)

    assert imem.read(0) == 0
    imem.update()
    assert imem.read(1) == 0
