from abc import abstractmethod

from .itrigger import ITrigger

class BaseMem(ITrigger):
    def __init__(self, size_bytes: int):
        self.size_bytes: int = size_bytes
        self._memory: list[int] = [0] * size_bytes

    def _validate_address(self, address: int) -> None:
        if not (0 <= address < self.size_bytes):
            raise IndexError(f"Address 0x{address:X} out of memory bounds (size: {self.size_bytes} bytes)")

    def read(self, address: int) -> int:
        self._validate_address(address)
        return self._memory[address]

    @abstractmethod
    def set(self, address: int, value: int) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass