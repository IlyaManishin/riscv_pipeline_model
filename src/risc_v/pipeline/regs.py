from dataclasses import dataclass

import risc_v.riscv_config as conf

from sim_base.mem.register import Register
from sim_base.mem.register import ITrigger

from risc_v.modules.pc import PC
from risc_v.modules.mem.reg_file import RegFile
from risc_v.modules.mem.imem import InstrMem
from risc_v.modules.mem.dmem import DataMem


pc = PC()
rf = RegFile()
imem = InstrMem(conf.IMEM_ADDR_BYTE_WIDTH - conf.BYTE_ADDR_WIDTH)
dmem = DataMem(conf.DMEM_ADDR_BYTE_WIDTH - conf.BYTE_ADDR_WIDTH)


# if_id = IF_ID_Stage()
# id_ex = ID_EX_Stage()
# ex_mem = EX_MEM_Stage()
# mem_wb = MEM_WB_Stage()

# pipeline_triggers: list[ITrigger] = [
#     pc.reg,
#     rf,
#     imem,
#     dmem,
#     *if_id.get_triggers(),
#     *id_ex.get_triggers(),
#     *ex_mem.get_triggers(),
#     *mem_wb.get_triggers()
# ]

# Core.clk().add_triggers(pipeline_triggers)
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

    def get_triggers(self) -> list[ITrigger]:
        return [
            self.alu_out, self.rf_rd2, self.rd,
            self.wb_sel, self.reg_wr, self.dmem_sel
        ]


@dataclass
class MEM_WB_Stage:
    alu_out: Register = Register()
    dmem_data: Register = Register()
    rd: Register = Register()
    wb_sel: Register = Register()
    reg_wr: Register = Register()

    def get_triggers(self) -> list[ITrigger]:
        return [
            self.alu_out, self.dmem_data, self.rd,
            self.wb_sel, self.reg_wr
        ]

