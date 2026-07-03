from .base_mem import BaseMem

class AsyncReadMem(BaseMem):
    def __init__(self, size: int, cell_size: int):
        super().__init__(size, cell_size)
        self._next_write: tuple[int, int] | None = None

    def read(self, address: int) -> int:
        self._validate_address(address)
        return self._memory[address]

    def write(self, address: int, value: int) -> None:
        self._validate_address(address)
        if self._next_write is not None:
            raise RuntimeError("Memory write conflict: multiple writes detected within a single clock cycle")
        self._next_write = (address, value & self._mask)

    def update(self) -> None:
        if self._next_write is not None:
            addr, val = self._next_write
            self._memory[addr] = val
            self._next_write = None