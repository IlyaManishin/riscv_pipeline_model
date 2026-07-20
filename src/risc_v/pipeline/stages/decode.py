import risc_v.riscv_config as conf
import risc_v.pipeline.regs as regs

from risc_v.modules.decode import Instruction_Decoder
from risc_v.modules.immgen import ImmGen
from risc_v.modules.branch_unit import BranchUnit
from risc_v.modules.mem.reg_file import RegFile


class Decode:
    def __init__(self, rf: RegFile, buff_if_id: regs.IF_ID_Stage, buff_id_ex: regs.ID_EX_Stage):
        self.rf_inst = rf
        self.buff_if_id = buff_if_id
        self.buff_id_ex = buff_id_ex
        self.id_controls = None
        self.instr = None
        self.br_eq = 0
        self.br_lt = 0
        self.rs1 = 0
        self.rs2 = 0
        self.rd = 0
        self.rf_rd1 = 0
        self.rf_rd2 = 0
        self.pc = 0
        self.imm = 0
        self.imm_pc = 0
        self.jfid = 0
        self.valid = 0

    def update(self):
        self.instr = conf.Instruction(self.buff_if_id.instr.read())

        self.pc = self.buff_if_id.pc.read()

        self.rs1 = self.instr.rs1
        self.rs2 = self.instr.rs2
        self.rd = self.instr.rd

        self.rf_rd1 = self.rf_inst.read(self.rs1)
        self.rf_rd2 = self.rf_inst.read(self.rs2)

        self.id_controls = Instruction_Decoder.decode(self.instr)
        self.br_eq, self.br_lt = BranchUnit.compare(
            self.rf_rd1, self.rf_rd2, bool(self.id_controls.br_un))
        self.id_controls = Instruction_Decoder.decode(
            self.instr, self.br_eq, self.br_lt)

        self.imm = ImmGen.generate(self.instr, self.id_controls.imm_type)
        self.imm_pc = self.pc + self.imm

        self.buff_id_ex.pc.set(self.pc)
        self.buff_id_ex.rf_rd1.set(self.rf_rd1)
        self.buff_id_ex.rf_rd2.set(self.rf_rd2)
        self.buff_id_ex.imm.set(self.imm)
        self.buff_id_ex.rs1.set(self.instr.rs1)
        self.buff_id_ex.rs2.set(self.instr.rs2)
        self.buff_id_ex.rd.set(self.rd)
        self.buff_id_ex.alu_sel.set(self.id_controls.alu_sel.value)
        self.buff_id_ex.a_sel.set(self.id_controls.a_sel)
        self.buff_id_ex.b_sel.set(self.id_controls.b_sel)
        self.buff_id_ex.wb_sel.set(self.id_controls.wb_sel)
        self.buff_id_ex.reg_wr.set(self.id_controls.reg_wr)
        self.buff_id_ex.dmem_sel.set(self.id_controls.dmem_sel.to_int())
        self.buff_id_ex.jfexe.set(self.id_controls.jf_exe)
        self.buff_id_ex.alushift_sel.set(self.id_controls.alushift_sel)
        self.buff_id_ex.shift_sel.set(self.id_controls.sh_sel)

        self.jfid = not bool(self.id_controls.pc_sel)

        self.valid = self.buff_if_id.valid.read()
        self.buff_id_ex.valid.set(self.valid)
