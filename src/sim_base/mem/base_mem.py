from abc import abstractmethod

from ..core.itrigger import ITrigger


class BaseMem(ITrigger):
    def __init__(self, size: int, cell_size: int):
        self._size: int = size
        self._cell_size: int = cell_size

        self._cell_mask: int = (1 << cell_size) - 1
        self._memory: list[int] = [0] * size

    def get_size(self) -> int:
        return self._size

    def get_cell_size(self) -> int:
        return self._cell_size

    def _validate_address(self, addr: int) -> None:
        if addr < 0 or addr >= self._size:
            raise IndexError(
                f"Address {addr} out of memory bounds (size: {self._size} cells)")

    def _read_cell(self, addr: int):
        self._validate_address(addr)
        return self._memory[addr]
    
    def _write_cell(self, addr: int, value: int):
        self._validate_address(addr)
        self._memory[addr] = value & self._cell_mask

    @abstractmethod
    def read(self, addr: int) -> int:
        pass

    @abstractmethod
    def write(self, addr: int, value: int) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass
