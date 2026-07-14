from sim_base.mem.block_mem import BlockMem
from risc_v import riscv_config as conf


class InstrMem(BlockMem):
    def __init__(self,
                 addr_width: int = conf.IMEM_ADDR_BYTE_WIDTH - conf.BYTE_ADDR_WIDTH,
                 cell_size: int = conf.XLEN):
        super().__init__(addr_width, cell_size, True)

    def write(self, addr: int, value: int, byte_we: int | None = None) -> None:
        raise PermissionError(
            "Instruction Memory is read-only during simulation execution")

    def load_program(self, program_code: list[int]) -> None:
        if len(program_code) > self._size:
            raise ValueError(
                "Program size exceeds Instruction Memory capacity")
        for addr, instr in enumerate(program_code):
            self._memory[addr*5] = instr & self._cell_mask
