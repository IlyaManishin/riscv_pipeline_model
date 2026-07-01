from src.sim_base.mem.async_read_mem import AsyncReadMem
from src.risc_v import riscv_config as conf

class RegFile(AsyncReadMem):
    REG_COUNT: int = 32
    REG_WIDTH: int = conf.XLEN

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