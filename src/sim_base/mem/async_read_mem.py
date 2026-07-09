from .base_mem import BaseMem

class AsyncReadMem(BaseMem):
    """
    Asynchronous-read synchronous-write memory.

    Notes:
        * Reads are asynchronous (combinational) with no single-cycle access restrictions.
        * Allow many reads and only 1 write per cycle.
        * Writes are deferred and committed to memory only when `update()` is called.
    """
    def __init__(self, size: int, cell_size: int):
        super().__init__(size, cell_size)
        self._next_write: tuple[int, int] | None = None

    def read(self, address: int) -> int:
        return self._read_cell(address)

    def write(self, address: int, value: int) -> None:
        if self._next_write is not None:
            raise RuntimeError("Memory write conflict: multiple writes detected within a single clock cycle")
        self._next_write = (address, value)

    def update(self) -> None:
        if self._next_write is not None:
            addr, val = self._next_write
            self._write_cell(addr, val)
            self._next_write = None