from sim_base.mem.register import Register

from risc_v.modules.pc import PC
from risc_v.mem.pl.imem import InstrMem

from models.pipeline import regs


class Fetch:
    def __init__(self, pc: PC, imem: InstrMem, buff_if_id: regs.IF_ID_Stage,
                 jfid_E: Register[bool], jfpc_E: Register[int],
                 jfexe_M: Register[bool], jfpc_M: Register[int]):
        ########## INPUT SIGNALS ##########
        self.pc_instr: PC = pc
        self.imem: InstrMem = imem
        self.jfid_E: Register[bool] = jfid_E
        self.jfpc_E: Register[int] = jfpc_E
        self.jfexe_M: Register[bool] = jfexe_M
        self.jfpc_M: Register[int] = jfpc_M

        ########## OUTPUT SIGNALS ##########
        self.buff_if_id: regs.IF_ID_Stage = buff_if_id

        ########## DEBUG SIGNALS ##########
        self.valid: bool = False
        self.br_taken: bool = False

        self.pc: int = 0
        self.pc_next: int = 0

    def update(self) -> None:
        # ===== Branch/Jump Mux =====
        if self.jfexe_M.read():
            self.br_taken = True
            pc_br = self.jfpc_M.read()
        elif self.jfid_E.read():
            self.br_taken = True
            pc_br = self.jfpc_E.read()
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
        self.buff_if_id.write(pc=self.pc_next, valid=self.valid)

    def pc_stall(self):
        self.pc_instr.set_pc(True, self.pc_instr.read())

    def stall(self):
        self.buff_if_id.stall()

    def flush(self):
        self.buff_if_id.flush()
