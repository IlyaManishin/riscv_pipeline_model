import risc_v.riscv_config as conf
from risc_v.pipeline import regs

from risc_v.modules.pc import PC

from risc_v.modules.mem.imem import InstrMem

class Fetch:
    
    def __init__(self, pc: PC, imem: InstrMem, buff_if_id: regs.IF_ID_Stage):
        self.buff_if_id = buff_if_id
        self.pc_instr = pc
        self.imem = imem
        self.stall_pc = 0
        self.valid = 0
        self.pc = 0
    def update(self, jfexe: int, jfid: int, alures: int,  imm_pc: int):
        self.buff_if_id.pc.set(self.pc_instr.read())
        self.buff_if_id.instr.set(self.imem.read(self.pc_instr.read() >> 2))
        
        self.valid = 1
        self.buff_if_id.valid.set(self.valid)
        
        self.pc = self.pc_instr.read()
        
        if self.stall_pc:
            self.pc_instr.set_pc(True, self.pc_instr.read())
        elif jfid:
            self.pc_instr.set_pc(True, imm_pc)
        elif jfexe:
            self.pc_instr.set_pc(True, alures)
        else:
            self.pc_instr.set_pc(False, 0)
    
    def stall(self):
        self.stall_pc = 1
    def unstall(self):
        self.stall_pc = 0