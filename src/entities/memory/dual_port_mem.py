from ..core.mem import BaseMem

class DualPortMem(BaseMem):
    def __init__(self, size_bytes: int):
        super().__init__(size_bytes)
        self._next_write: tuple[int, int] | None = None

    def set(self, address: int, value: int) -> None:
        self._validate_address(address)
        if self._next_write is not None:
            raise RuntimeError("Memory access conflict: multiple writes detected within a single clock cycle")
        self._next_write = (address, value)

    def update(self) -> None:
        if self._next_write is not None:
            addr, val = self._next_write
            self._memory[addr] = val
            self._next_write = None