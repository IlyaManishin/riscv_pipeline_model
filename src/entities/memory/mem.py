from ..core.itrigger import ITrigger

class Mem(ITrigger):
    def __init__(self, size_bytes: int):
        self.size_bytes: int = size_bytes
        self._memory: list[int] = [0] * size_bytes
        self._next_write: tuple[int, int] | None = None

    def _validate_address(self, address: int) -> None:
        if not (0 <= address < self.size_bytes):
            raise IndexError(f"Address 0x{address:X} out of memory bounds (size: {self.size_bytes} bytes)")

    def set(self, address: int, value: int) -> None:
        self._validate_address(address)
        if self._next_write is not None:
            raise RuntimeError(f"Memory access conflict: multiple writes detected within a single clock cycle")
        self._next_write = (address, value)

    def update(self) -> None:
        if self._next_write is not None:
            addr, val = self._next_write
            self._memory[addr] = val
            self._next_write = None

    def read(self, address: int) -> int:
        self._validate_address(address)
        return self._memory[address]