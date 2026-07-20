import risc_v.riscv_config as conf
from risc_v.pipeline import regs

from risc_v.modules.pc import PC

from risc_v.modules.mem.imem import InstrMem


import risc_v.riscv_config as conf
from risc_v.pipeline import regs
from risc_v.modules.pc import PC
from risc_v.modules.mem.imem import InstrMem


class Fetch:
    def __init__(self, pc: PC, imem: InstrMem, buff_if_id: regs.IF_ID_Stage):
        # --- Dependencies ---
        self.buff_if_id: regs.IF_ID_Stage = buff_if_id
        self.pc_instr: PC = pc
        self.imem: InstrMem = imem

        # --- Control Signals ---
        self.stall_pc: bool = False
        self.valid: bool = False

        # --- Data Path ---
        self.pc: int = 0

    def update(self, jfexe: int, jfid: int, alures: int,  imm_pc: int):
        self.buff_if_id.pc.set(self.pc_instr.read())
        self.buff_if_id.instr.set(self.imem.read(self.pc_instr.read() >> 2))

        self.valid = True
        self.buff_if_id.valid.set(self.valid)

        self.pc = self.pc_instr.read()

        if jfid:
            self.pc_instr.set_pc(True, imm_pc)
        elif jfexe:
            self.pc_instr.set_pc(True, alures)
        else:
            self.pc_instr.set_pc(False, 0)

    def stall(self):
        self.pc_instr.set_pc(True, self.pc_instr.read())
        self.buff_if_id.stall()

    def flush(self):
        self.buff_if_id.flush()
