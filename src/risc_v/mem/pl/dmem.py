from sim_base.mem.block_mem import BlockMem
from risc_v import riscv_config as conf


class DataMem(BlockMem):
    def __init__(self,
                 addr_width: int = conf.DMEM_ADDR_BYTE_WIDTH - conf.BYTE_ADDR_WIDTH,
                 cell_size: int = conf.XLEN):
        super().__init__(addr_width, cell_size, True)

    def load_data(self, data: list[int]) -> None:
        if len(data) > self._size:
            raise ValueError(
                "The size of the data exceeds the amount of data memory")
        for addr, instr in enumerate(data):
            self._memory[addr] = instr & self._cell_mask
