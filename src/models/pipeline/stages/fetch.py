from sim_base.mem.register import Register

from risc_v.modules.pc import PC
from risc_v.mem.pl.imem import InstrMem

from models.pipeline import regs


class Fetch:
    def __init__(self, pc: PC,
                 imem: InstrMem, buff_if_id: regs.IF_ID_Stage,
                 ):
        # --- Dependencies ---
        self.buff_if_id: regs.IF_ID_Stage = buff_if_id
        self.pc_instr: PC = pc
        self.imem: InstrMem = imem

        # --- Control Signals ---
        self.stall_pc: bool = False
        self.valid: bool = False
        self.br_taken: bool = False

        # --- Data Path ---
        self.pc: Register[int] = 0
        self.pc_next: int = 0
        self.instr: int = 0

    def update(self, jfexe_m: int, jfpc_m: int, jfid_e: int, jfpc_e: int):
        # ===== Instruction Read =====
        self.instr = self.imem.read()

        # ===== Branch Target & Jump Multiplexing =====
        if jfexe_m:
            self.br_taken = True
            pc_br = jfpc_m
        elif jfid_e:
            self.br_taken = True
            pc_br = jfpc_e
        else:
            self.br_taken = False
            pc_br = 0

        self.pc = self.pc_instr.read()
        self.pc_next = pc_br if self.br_taken else self.pc + 4

        # ===== Program Counter & Instruction Memory Address Register =====
        self.pc_instr.set_pc(True, self.pc_next)
        self.imem.set(self.pc_next)

        # ===== IF/ID Pipeline Register =====
        self.valid = True
        self.buff_if_id.pc.set(self.pc_next)
        self.buff_if_id.instr.set(self.instr)
        self.buff_if_id.valid.set(self.valid)

    def stall(self):
        self.pc_instr.set_pc(True, self.pc_instr.read())
        self.buff_if_id.stall()

    def flush(self):
        self.buff_if_id.flush()
