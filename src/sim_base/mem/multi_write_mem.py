from .base.base_mem import BaseMem

class MultiWriteMem(BaseMem):
    def __init__(self, addr_width: int, cell_size: int, addr_overflow: bool = False):
        super().__init__(addr_width, cell_size, addr_overflow)
        self._transactions: list[tuple[int, int]] = []

    def read(self, addr: int) -> int:
        eff_addr = self._get_effective_addr(addr)
        return self._read_cell(eff_addr)

    def write(self, address: int, value: int) -> None:
        eff_addr = self._get_effective_addr(address)
        self._validate_address(eff_addr)
        self._transactions.append((eff_addr, value & self._cell_mask))

    def update(self) -> None:
        for addr, val in self._transactions:
            self._memory[addr] = val
        self._transactions.clear()