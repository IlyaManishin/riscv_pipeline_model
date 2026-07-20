import risc_v.riscv_config as conf
from sim_base.mem.register import Register
from sim_base.mem.register import ITrigger
from risc_v.modules.pc import PC
from risc_v.modules.mem.reg_file import RegFile
from risc_v.modules.mem.imem import InstrMem
from risc_v.modules.mem.dmem import DataMem


class IF_ID_Stage:
    pc: Register
    instr: Register
    valid: Register

    def __init__(self):
        self.pc = Register()
        self.instr = Register()
        self.valid = Register()

    def get_triggers(self) -> list[ITrigger]:
        return [self.pc, self.instr, self.valid]

    def stall(self):
        for r in self.get_triggers():
            r.set(r.read())

    def flush(self):
        self.instr.set(0)
        self.valid.set(0)


class ID_EX_Stage:
    pc: Register
    rf_rd1: Register
    rf_rd2: Register
    imm: Register
    rs1: Register
    rs2: Register
    rd: Register
    alu_sel: Register
    shift_sel: Register
    a_sel: Register
    b_sel: Register
    wb_sel: Register
    reg_wr: Register
    dmem_sel: Register
    jfexe: Register
    alushift_sel: Register
    valid: Register

    def __init__(self):
        self.pc = Register()
        self.rf_rd1 = Register()
        self.rf_rd2 = Register()
        self.imm = Register()
        self.rs1 = Register()
        self.rs2 = Register()
        self.rd = Register()
        self.alu_sel = Register()
        self.shift_sel = Register()
        self.a_sel = Register()
        self.b_sel = Register()
        self.wb_sel = Register()
        self.reg_wr = Register()
        self.dmem_sel = Register()
        self.jfexe = Register()
        self.alushift_sel = Register()
        self.valid = Register()

    def get_triggers(self) -> list[ITrigger]:
        return [
            self.pc, self.rf_rd1, self.rf_rd2, self.imm,
            self.rs1, self.rs2, self.rd,
            self.alu_sel, self.a_sel, self.b_sel, self.wb_sel, self.reg_wr, self.dmem_sel,
            self.jfexe, self.alushift_sel, self.valid, self.shift_sel
        ]

    def stall(self):
        for r in self.get_triggers():
            r.set(r.read())

    def flush(self):
        self.jfexe.set(0)
        self.reg_wr.set(0)
        self.dmem_sel.set(0)
        self.valid.set(0)


class EX_MEM_Stage:
    alu_out: Register
    rf_rd2: Register
    rd: Register
    wb_sel: Register
    reg_wr: Register
    dmem_sel: Register
    pc4: Register
    valid: Register

    def __init__(self):
        self.alu_out = Register()
        self.rf_rd2 = Register()
        self.rd = Register()
        self.wb_sel = Register()
        self.reg_wr = Register()
        self.dmem_sel = Register()
        self.pc4 = Register()
        self.valid = Register()

    def get_triggers(self) -> list[ITrigger]:
        return [
            self.alu_out, self.rf_rd2, self.rd,
            self.wb_sel, self.reg_wr, self.dmem_sel, self.pc4, self.valid
        ]


class MEM_WB_Stage:
    alu_out: Register
    dmem_data: Register
    rd: Register
    wb_sel: Register
    reg_wr: Register
    pc4: Register
    valid: Register

    def __init__(self):
        self.alu_out = Register()
        self.dmem_data = Register()
        self.rd = Register()
        self.wb_sel = Register()
        self.reg_wr = Register()
        self.pc4 = Register()
        self.valid = Register()

    def get_triggers(self) -> list[ITrigger]:
        return [
            self.alu_out, self.dmem_data, self.rd,
            self.wb_sel, self.reg_wr, self.pc4, self.valid
        ]
