import risc_v.riscv_config as conf
import risc_v.pipeline.regs as regs

from risc_v.modules.alu import Alu
from risc_v.modules.shifter import Shifter
from risc_v.riscv_config import Alu_sel_t, Shift_sel_t


class Execute:
    def __init__(self, buff_id_ex: regs.ID_EX_Stage, buff_ex_mem: regs.EX_MEM_Stage):
        self.buff_id_ex = buff_id_ex
        self.buff_ex_mem = buff_ex_mem
        self.reg_wr = 0
        self.alures = 0
        self.shres = 0
        self.jfexe = 0
        self.rd1 = 0
        self.rd2 = 0
        self.alu_in_a = 0
        self.alu_in_b = 0
        self.shift_shamt = 0
        self.rd = 0
        self.valid = 0
        self.pc4 = 0

    def update(self):
        self.rd1 = self.buff_id_ex.rf_rd1.read()
        self.rd2 = self.buff_id_ex.rf_rd2.read()

        self.alu_in_a = self.rd1 if self.buff_id_ex.a_sel.read() else self.buff_id_ex.pc.read()
        self.alu_in_b = self.rd2 if self.buff_id_ex.b_sel.read() else self.buff_id_ex.imm.read()

        self.alures = Alu.execute(Alu_sel_t(self.buff_id_ex.alu_sel.read()),
                                  self.alu_in_a, self.alu_in_b)

        self.shift_shamt = (self.rd2 & 0x1F) if self.buff_id_ex.b_sel.read() else (
            self.buff_id_ex.rs2.read() & 0x1F)
        self.shres = Shifter.shift(sel=Shift_sel_t(self.buff_id_ex.shift_sel.read()),
                                   data=self.alu_in_a,
                                   shamt=self.shift_shamt)


        self.buff_ex_mem.alu_out.set(
            self.shres if self.buff_id_ex.alushift_sel.read() else self.alures)
        self.buff_ex_mem.rf_rd2.set(self.rd2)
        self.rd = self.buff_id_ex.rd.read()
        self.buff_ex_mem.rd.set(self.rd)
        self.buff_ex_mem.wb_sel.set(self.buff_id_ex.wb_sel.read())

        self.reg_wr = self.buff_id_ex.reg_wr.read()
        self.buff_ex_mem.reg_wr.set(self.reg_wr)

        self.buff_ex_mem.dmem_sel.set(self.buff_id_ex.dmem_sel.read())
        self.pc4 = self.buff_id_ex.pc.read() + 4
        self.buff_ex_mem.pc4.set(self.pc4)
        self.jfexe = self.buff_id_ex.jfexe.read()

        self.valid = self.buff_id_ex.valid.read()
        self.buff_ex_mem.valid.set(self.valid)
