from ..core.mem import BaseMem

class MultiWriteMem(BaseMem):
    def __init__(self, size: int, cell_size: int):
        super().__init__(size, cell_size)
        self._transactions: list[tuple[int, int]] = []

    def write(self, address: int, value: int) -> None:
        self._validate_address(address)
        self._transactions.append((address, value & self._mask))

    def update(self) -> None:
        for addr, val in self._transactions:
            self._memory[addr] = val
        self._transactions.clear()