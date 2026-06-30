from src.base_entities.memory.block_mem import BlockMem
from src import riscv_config as conf
 
class InstrMem(BlockMem):
    def __init__(self, size: int, cell_size: int = conf.XLEN):
        super().__init__(size, cell_size)

    def write(self, address: int, value: int) -> None:
        raise PermissionError("Instruction Memory is read-only during simulation execution")

    def load_program(self, program_code: list[int]) -> None:
        if len(program_code) > self.size:
            raise ValueError("Program size exceeds Instruction Memory capacity")
        for addr, instr in enumerate(program_code):
            self._memory[addr] = instr & self._mask