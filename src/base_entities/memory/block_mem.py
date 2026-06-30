from .async_read_mem import AsyncReadMem

class BlockMem(AsyncReadMem):
    def __init__(self, size: int, cell_size: int):
        super().__init__(size, cell_size)
        self._current_read_data: int = 0
        self._next_read_addr: int | None = None

    def read(self, address: int) -> int:
        self._validate_address(address)
        self._next_read_addr = address
        return self._current_read_data

    def update(self) -> None:
        if self._next_read_addr is not None:
            self._current_read_data = self._memory[self._next_read_addr]
            self._next_read_addr = None
        
        super().update()