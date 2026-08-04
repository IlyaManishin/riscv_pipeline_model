from sim_base.mem.lut_memory import LutMemory
from risc_v import riscv_config as conf

class RegFile(LutMemory):
    REG_COUNT: int = 32
    REG_WIDTH: int = conf.XLEN

    def __init__(self, size: int = REG_COUNT, cell_size: int = REG_WIDTH):
        super().__init__(size, cell_size)

    def read(self, addr: int) -> int:
        if addr == 0:
            return 0
        return super().read(addr)

    def update(self) -> None:
        super().update()
        self._memory[0] = 0