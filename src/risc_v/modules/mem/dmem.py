from sim_base.mem.block_mem import BlockMem
from risc_v import riscv_config as conf

class DataMem(BlockMem):
    def __init__(self, size: int, cell_size: int = conf.XLEN):
        super().__init__(size, cell_size)
