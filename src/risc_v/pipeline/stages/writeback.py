import risc_v.riscv_config as conf
import risc_v.pipeline.regs as regs

from sim_base.mem.register import Register

from risc_v.modules.mem.reg_file import RegFile


class WriteBack:

    def __init__(self, rf: RegFile, buff_mem_wb: regs.MEM_WB_Stage, rst_reg: Register):
        self.rf_inst = rf
        self.buff_mem_wb = buff_mem_wb
        self.rst_reg = rst_reg

        self.rf_wd3 = 0
        self.rf_we3 = False

    def update(self):
        match conf.WB_sel_t(self.buff_mem_wb.wb_sel.read()):
            case conf.WB_sel_t.PC4_OUT:
                self.rf_wd3 = self.buff_mem_wb.pc4.read()
            case conf.WB_sel_t.ALU_OUT:
                self.rf_wd3 = self.buff_mem_wb.alu_out.read()
            case conf.WB_sel_t.SHIFTER_OUT:
                self.rf_wd3 = self.buff_mem_wb.alu_out.read()
            case conf.WB_sel_t.DMEM_OUT:
                self.rf_wd3 = self.buff_mem_wb.dmem_data.read()
            case _:
                self.rf_wd3 = 0

        self.rf_we3 = bool(self.buff_mem_wb.reg_wr.read()) and not bool(self.rst_reg.read())
        if self.rf_we3:
            self.rf_inst.write(self.buff_mem_wb.rd.read(), self.rf_wd3)
