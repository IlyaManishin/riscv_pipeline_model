from dataclasses import dataclass

import risc_v.riscv_config as conf

from sim_base.mem.register import Register
from sim_base.mem.register import ITrigger

from risc_v.modules.pc import PC
from risc_v.modules.mem.reg_file import RegFile
from risc_v.modules.mem.imem import InstrMem
from risc_v.modules.mem.dmem import DataMem


# Module-level singleton scaffolding (kept for reference; instances are
# instead created and wired together in cpu_system.py).
# pc = PC(...)
# rf = RegFile()
# imem = InstrMem(...)
# dmem = DataMem(...)

@dataclass
class IF_ID_Stage:
    pc: Register = Register()
    instr: Register = Register()

    def get_triggers(self) -> list[ITrigger]:
        return [self.pc, self.instr]
    
    def stall(self):
        for r in self.get_triggers():
            r.set(r.read())
    def flush(self):
        self.instr.set(0)


@dataclass
class ID_EX_Stage:
    pc: Register = Register()
    rf_rd1: Register = Register()
    rf_rd2: Register = Register()
    imm: Register = Register()
    rs1: Register = Register()
    rs2: Register = Register()
    rd: Register = Register()
    alu_sel: Register = Register()
    a_sel: Register = Register()
    b_sel: Register = Register()
    wb_sel: Register = Register()
    reg_wr: Register = Register()
    dmem_sel: Register = Register()
    jfexe: Register = Register()
    alushift_sel: Register = Register()

    def get_triggers(self) -> list[ITrigger]:
        return [
            self.pc, self.rf_rd1, self.rf_rd2, self.imm,
            self.rs1, self.rs2, self.rd,
            self.alu_sel, self.a_sel, self.b_sel, self.wb_sel, self.reg_wr, self.dmem_sel,
            self.jfexe, self.alushift_sel
        ]
    def stall(self):
        for r in self.get_triggers():
            r.set(r.read())
    def flush(self):
        self.jfexe.set(0)
        self.reg_wr.set(0)
        self.dmem_sel.set(0)
        


@dataclass
class EX_MEM_Stage:
    alu_out: Register = Register()
    rf_rd2: Register = Register()
    rd: Register = Register()
    wb_sel: Register = Register()
    reg_wr: Register = Register()
    dmem_sel: Register = Register()
    pc4: Register = Register()

    def get_triggers(self) -> list[ITrigger]:
        return [
            self.alu_out, self.rf_rd2, self.rd,
            self.wb_sel, self.reg_wr, self.dmem_sel, self.pc4
        ]


@dataclass
class MEM_WB_Stage:
    alu_out: Register = Register()
    dmem_data: Register = Register()
    rd: Register = Register()
    wb_sel: Register = Register()
    reg_wr: Register = Register()
    pc4: Register = Register()

    def get_triggers(self) -> list[ITrigger]:
        return [
            self.alu_out, self.dmem_data, self.rd,
            self.wb_sel, self.reg_wr, self.pc4
        ]

