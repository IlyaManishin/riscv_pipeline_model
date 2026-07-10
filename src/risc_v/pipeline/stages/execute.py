import risc_v.riscv_config as conf
import risc_v.pipeline.regs as regs

from risc_v.modules.alu import Alu
from risc_v.modules.shifter import Shifter


class Execute:
    def __init__(self, buff_id_ex: regs.ID_EX_Stage, buff_ex_mem: regs.EX_MEM_Stage):
        self.buff_id_ex = buff_id_ex
        self.buff_ex_mem = buff_ex_mem
        self.reg_wr = 0
        self.alures = 0
        self.alu_in_a = 0
        self.alu_in_b = 0
    
        