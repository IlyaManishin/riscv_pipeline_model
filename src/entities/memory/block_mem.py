from ..core.itrigger import ITrigger

class BlockMemory(ITrigger):
    def __init__(self, size_bytes: int):
        self.size_bytes: int = size_bytes
        self._memory: dict[int, int] = {}
        self._transactions: list[tuple[int, int]] = []

    def _validate_address(self, address: int) -> None:
        if not (0 <= address < self.size_bytes):
            raise IndexError(f"Address 0x{address:X} out of memory bounds (size: {self.size_bytes} bytes)")

    def set(self, address: int, value: int) -> None:
        self._validate_address(address)
        self._transactions.append((address, value))

    def update(self) -> None:
        for addr, val in self._transactions:
            self._memory[addr] = val
        self._transactions.clear()

    def read(self, address: int) -> int:
        self._validate_address(address)
        return self._memory.get(address, 0)