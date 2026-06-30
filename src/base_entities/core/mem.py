from abc import abstractmethod

from .itrigger import ITrigger

class BaseMem(ITrigger):
    def __init__(self, size: int, cell_size: int):
        self.size: int = size
        self.cell_size: int = cell_size
        
        self._mask: int = (1 << cell_size) - 1
        self._memory: list[int] = [0] * size

    def _validate_address(self, address: int) -> None:
        if not (0 <= address < self.size):
            raise IndexError(f"Address {address} out of memory bounds (size: {self.size} cells)")

    def read(self, address: int) -> int:
        self._validate_address(address)
        return self._memory[address]

    @abstractmethod
    def write(self, address: int, value: int) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass