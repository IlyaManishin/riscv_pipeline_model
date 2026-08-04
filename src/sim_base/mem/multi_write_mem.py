from .base.memory_array import MemoryArray

class MultiWriteMem(MemoryArray):
    def __init__(self, addr_width: int, cell_size: int, addr_overflow: bool = False):
        super().__init__(addr_width, cell_size, addr_overflow)
        self._transactions: list[tuple[int, int]] = []

    def read(self, addr: int) -> int:
        return self._read_cell(addr)

    def write(self, address: int, value: int) -> None:
        self._transactions.append((address, value))

    def update(self) -> None:
        for addr, val in self._transactions:
            self._write_cell(addr, val)
        self._transactions.clear()