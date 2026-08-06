from sim_base.mem.register import Register

from risc_v.modules.pc import PC
from risc_v.mem.pl.imem import InstrMem

from models.pipeline import regs


class Fetch:
    def __init__(self, pc: PC, imem: InstrMem, buff_if_id: regs.IF_ID_Stage):
        ########## INPUT SIGNALS ##########
        self.pc_instr: PC = pc
        self.imem: InstrMem = imem

        ########## OUTPUT SIGNALS ##########
        self.buff_if_id: regs.IF_ID_Stage = buff_if_id

        ########## DEBUG SIGNALS ##########
        self.stall_pc: bool = False
        self.valid: bool = False
        self.br_taken: bool = False

        self.pc: int = 0
        self.pc_next: int = 0

    def update(self,
               jfid_e: Register[bool], jfpc_e: Register[int],
               jfexe_m: Register[bool], jfpc_m: Register[int]) -> None:
        # ===== Branch/Jump Mux =====
        if jfexe_m.read():
            self.br_taken = True
            pc_br = jfpc_m.read()
        elif jfid_e.read():
            self.br_taken = True
            pc_br = jfpc_e.read()
        else:
            self.br_taken = False
            pc_br = 0

        # ===== PC & IMEM Address =====
        self.pc = self.pc_instr.read()
        self.pc_next = pc_br if self.br_taken else self.pc + 4

        self.pc_instr.set_pc(True, self.pc_next)
        self.imem.set(self.pc_next)

        # ===== IF/ID Pipeline Register =====
        self.valid = True
        self.buff_if_id.pc.set(self.pc_next)
        self.buff_if_id.valid.set(self.valid)

    def stall(self):
        self.pc_instr.set_pc(True, self.pc_instr.read())
        self.buff_if_id.stall()

    def flush(self):
        self.buff_if_id.flush()
