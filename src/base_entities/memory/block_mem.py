from ..core.mem import BaseMem

class BlockMem(BaseMem):
    def __init__(self, size: int, cell_size: int):
        super().__init__(size, cell_size)
        self._next_write: tuple[int, int] | None = None
        self._has_read_this_cycle: bool = False

    def read(self, address: int) -> int:
        self._validate_address(address)
        if self._has_read_this_cycle:
            raise RuntimeError("Memory read conflict: multiple reads detected within a single clock cycle")
        
        self._has_read_this_cycle = True
        return self._memory[address]

    def write(self, address: int, value: int) -> None:
        self._validate_address(address)
        if self._next_write is not None:
            raise RuntimeError("Memory write conflict: multiple writes detected within a single clock cycle")
        self._next_write = (address, value & self._mask)

    def update(self) -> None:
        self._has_read_this_cycle = False
        
        if self._next_write is not None:
            addr, val = self._next_write
            self._memory[addr] = val
            self._next_write = None