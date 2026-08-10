import pytest

from sim_base.mem.lut_memory import LutMemory
from sim_base.mem.multi_write_mem import MultiWriteMem
from sim_base.mem.async_block_mem import AsyncBlockMem
from sim_base.mem.block_mem import BlockMem

from risc_v.mem.reg_file import RegFile


class TestLutMemory:
    def test_initial_state_is_zero(self):
        mem = LutMemory(size=8, cell_size=16)
        for addr in range(8):
            assert mem.read(addr) == 0

    def test_value_masking(self):
        mem = LutMemory(size=4, cell_size=8)
        mem.write(0, 0x1FF)
        mem.update()
        assert mem.read(0) == 0xFF

    def test_deferred_write(self):
        mem = LutMemory(size=4, cell_size=32)
        mem.write(2, 0xABC)
        assert mem.read(2) == 0
        mem.update()
        assert mem.read(2) == 0xABC

    def test_write_conflict_same_cycle(self):
        mem = LutMemory(size=4, cell_size=32)
        mem.write(1, 100)
        with pytest.raises(RuntimeError):
            mem.write(1, 200)

    def test_write_conflict_different_addrs(self):
        mem = LutMemory(size=4, cell_size=32)
        mem.write(0, 10)
        with pytest.raises(RuntimeError):
            mem.write(1, 20)

    def test_out_of_bounds_read(self):
        mem = LutMemory(size=4, cell_size=32)
        with pytest.raises(IndexError):
            mem.read(4)

    def test_out_of_bounds_write(self):
        mem = LutMemory(size=4, cell_size=32)
        with pytest.raises(IndexError):
            mem.write(-1, 10)

    def test_multiple_cycles_sequence(self):
        mem = LutMemory(size=8, cell_size=32)
        for i in range(5):
            mem.write(i, (i + 1) * 10)
            mem.update()
        for i in range(5):
            assert mem.read(i) == (i + 1) * 10


class TestMultiWriteMem:
    def test_multiple_writes_same_cycle(self):
        mem = MultiWriteMem(addr_width=4, cell_size=32)
        mem.write(0, 10)
        mem.write(1, 20)
        mem.write(2, 30)
        assert mem.read(0) == 0
        assert mem.read(1) == 0
        assert mem.read(2) == 0
        mem.update()
        assert mem.read(0) == 10
        assert mem.read(1) == 20
        assert mem.read(2) == 30

    def test_write_override_order(self):
        mem = MultiWriteMem(addr_width=4, cell_size=32)
        mem.write(1, 100)
        mem.write(1, 200)
        mem.write(1, 300)
        mem.update()
        assert mem.read(1) == 300


class TestAsyncBlockMem:
    def test_byte_write_enable_masks(self):
        mem = AsyncBlockMem(addr_width=4, cell_size=32)
        mem.write(0, 0x11223344)
        mem.update()
        assert mem.read(0) == 0x11223344

        mem.write(0, 0xAABBCCDD, byte_we=0b0001)
        mem.update()
        assert mem.read(0) == 0x112233DD

        mem.write(0, 0xAABBCCDD, byte_we=0b0100)
        mem.update()
        assert mem.read(0) == 0x11BB33DD

        mem.write(0, 0xFFFFFFFF, byte_we=0b1010)
        mem.update()
        assert mem.read(0) == 0xFFBBFFDD

    def test_byte_we_zero_does_nothing(self):
        mem = AsyncBlockMem(addr_width=4, cell_size=32)
        mem.write(0, 0x12345678)
        mem.update()
        mem.write(0, 0xFFFFFFFF, byte_we=0)
        mem.update()
        assert mem.read(0) == 0x12345678

    def test_byte_we_invalid_range(self):
        mem = AsyncBlockMem(addr_width=4, cell_size=32)
        with pytest.raises(ValueError):
            mem.write(0, 0xFFFFFFFF, byte_we=0b10000)
        with pytest.raises(ValueError):
            mem.write(0, 0xFFFFFFFF, byte_we=-1)

    def test_addr_overflow_toggle(self):
        mem_no_overflow = AsyncBlockMem(addr_width=2, cell_size=16, addr_overflow=False)
        with pytest.raises(IndexError):
            mem_no_overflow.write(4, 100)

        mem_overflow = AsyncBlockMem(addr_width=2, cell_size=16, addr_overflow=True)
        mem_overflow.write(4, 100)
        mem_overflow.update()
        assert mem_overflow.read(0) == 100

    def test_metadata_getters(self):
        mem = AsyncBlockMem(addr_width=8, cell_size=64)
        assert mem.get_addr_width() == 8
        assert mem.get_size() == 256
        assert mem.get_cell_size() == 64


class TestBlockMem:
    def test_two_phase_registered_read(self):
        mem = BlockMem(addr_width=4, cell_size=32)
        mem.write(0, 0xAAAA)
        with pytest.raises(RuntimeError):
            mem.write(1, 0xBBBB)
        mem.update()

        assert mem.read() == 0
        mem.set_address(0)
        assert mem.read() == 0
        mem.update()
        assert mem.read() == 0xAAAA

        mem.write(1, 0xBBBB)
        mem.set(0)
        assert mem.read() == 0xAAAA
        mem.update()
        assert mem.read() == 0xAAAA

    def test_simultaneous_read_and_write(self):
        mem = BlockMem(addr_width=4, cell_size=32)
        mem.write(2, 0xFEED)
        mem.set(2)
        mem.update()

        assert mem.read() == 0xFEED

        mem.write(2, 0xFACE)
        mem.set(2)
        assert mem.read() == 0xFEED
        mem.update()
        assert mem.read() == 0xFACE

    def test_retains_read_address_until_set(self):
        mem = BlockMem(addr_width=4, cell_size=32)
        mem.write(3, 777)
        mem.update()

        mem.set(3)
        mem.update()
        assert mem.read() == 777

        mem.update()
        mem.update()
        assert mem.read() == 777

    def test_block_mem_byte_we_integration(self):
        mem = BlockMem(addr_width=4, cell_size=32)
        mem.write(0, 0x11223344)
        mem.update()

        mem.write(0, 0x99999999, byte_we=0b1100)
        mem.set(0)
        mem.update()
        assert mem.read() == 0x99993344