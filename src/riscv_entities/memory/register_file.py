from src.base_entities.memory.async_read_mem import AsyncReadMem

class RegisterFile(AsyncReadMem):
    REG_COUNT: int = 32
    REG_WIDTH: int = 32

    def __init__(self, size: int = REG_COUNT, cell_size: int = REG_WIDTH):
        super().__init__(size, cell_size)
    
    def update(self) -> None:
        super().update()

        #reset r0 register
        self._memory[0] = 0

    def read(self, address: int) -> int:
        if address == 0:
            return 0
        return super().read(address)    