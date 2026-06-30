from ..core.mem import BaseMem

class MultiWriteMem(BaseMem):
    def __init__(self, size_bytes: int):
        super().__init__(size_bytes)
        self._transactions: list[tuple[int, int]] = []

    def set(self, address: int, value: int) -> None:
        self._validate_address(address)
        self._transactions.append((address, value))

    def update(self) -> None:
        for addr, val in self._transactions:
            self._memory[addr] = val
        self._transactions.clear()