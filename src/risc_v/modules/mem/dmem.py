from sim_base.mem.block_mem import BlockMem
from risc_v import riscv_config as conf

class DataMem(BlockMem):
    def __init__(self, size: int, cell_size: int = conf.XLEN):
        super().__init__(size, cell_size)
    
    def load_data(self, data: list[int]) -> None:
        if len(data) > self.size:
            raise ValueError("The size of the data exceeds the amount of data memory")
        for addr, instr in enumerate(data):
            self._memory[addr] = instr & self._mask
