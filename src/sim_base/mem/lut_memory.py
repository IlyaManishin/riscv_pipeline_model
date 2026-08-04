from .base.memory_array import MemoryArray

class LutMemory(MemoryArray):
    def __init__(self, size: int, cell_size: int):
        super().__init__(size, cell_size)
        self._next_write: tuple[int, int] | None = None

    def read(self, addr: int) -> int:
        return self._read_cell(addr)

    def write(self, addr: int, value: int) -> None:
        if self._next_write is not None:
            raise RuntimeError("Memory write conflict: multiple writes detected within a single clock cycle")

        self._validate_address(addr)
        self._next_write = (addr, value)

    def update(self) -> None:
        if self._next_write is not None:
            addr, val = self._next_write
            self._write_cell(addr, val)
            self._next_write = None