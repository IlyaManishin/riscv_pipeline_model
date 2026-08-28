from sim_base.mem.register import Register

from risc_v.modules.pc import PC
from risc_v.mem.pl.imem import InstrMem

from models.pipeline import regs


class Fetch:
    def __init__(self, pc: PC, imem: InstrMem,
                 buff_if_id: regs.IF_ID_Stage,
                 jfexe_M: Register[bool], jfpc_M: Register[int]):
        ########## INPUT SIGNALS ##########
        self.pc_inst: PC = pc
        self.imem: InstrMem = imem
        self.jfexe_M: Register[bool] = jfexe_M
        self.jfpc_M: Register[int] = jfpc_M

        ########## OUTPUT SIGNALS ##########
        self.buff_if_id: regs.IF_ID_Stage = buff_if_id

        ########## DEBUG SIGNALS ##########
        self.valid: bool = False

        self.pc: int = 0
        self.pc_next: int = 0
        self.is_pc_stall: bool = False

        self.is_stall: bool = False
        self.is_flush: bool = False

    def update(self) -> None:
        # ===== Branch/Jump Mux =====
        if self.jfexe_M.read():
            br_taken = True
            pc_br = self.jfpc_M.read()
        else:
            br_taken = False
            pc_br = 0

        # ===== PC & IMEM Address =====
        self.pc = self.pc_inst.read()
        self.pc_next = self.pc_inst.get_pc_next(br_taken, pc_br)
        self.pc_inst.set_pc(self.pc_next + 4)
        self.is_pc_stall = False

        word_imem_addr = self.pc_next >> 2
        self.imem.set(word_imem_addr)

        # ===== IF/ID Pipeline Register =====
        self.valid = True
        self.buff_if_id.pc.set(self.pc_next)
        self.buff_if_id.valid.set(self.valid)
        
        self.is_stall = False
        self.is_flush = False

    def pc_stall(self):
        self.is_pc_stall = True
        self.pc_next = self.pc_inst.read()
        self.pc_inst.stall()

    def stall(self):
        # flush has higher priority
        if self.is_flush:
            return
        
        self.imem.set(self.buff_if_id.pc.read() >> 2)

        self.buff_if_id.stall()
        self.is_stall = True

    def flush(self):
        self.buff_if_id.flush()
        self.is_flush = True

    def rst(self):
        self.flush()