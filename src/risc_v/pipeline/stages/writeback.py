import risc_v.riscv_config as conf
import risc_v.pipeline.regs as regs

from sim_base.mem.register import Register

from risc_v.modules.mem.reg_file import RegFile

import risc_v.riscv_config as conf
import risc_v.pipeline.regs as regs
from sim_base.mem.register import Register
from risc_v.modules.mem.reg_file import RegFile


class WriteBack:
    def __init__(self, rf: RegFile, buff_mem_wb: regs.MEM_WB_Stage, rst_reg: Register):
        # --- Зависимости (Dependencies) ---
        self.rf_inst: RegFile = rf
        self.buff_mem_wb: regs.MEM_WB_Stage = buff_mem_wb
        self.rst_reg: Register = rst_reg

        # --- Сигналы управления (Control Signals) ---
        self.rf_we3: bool = False
        self.valid: bool = False
        self.reg_wr: bool = False
        
        # --- Данные пути (Data Path) ---
        self.rf_wd3: int = 0
        self.pc4: int = 0
        self.rd: int = 0

    def update(self):
        self.pc4 = self.buff_mem_wb.pc4.read()
        match conf.WB_sel_t(self.buff_mem_wb.wb_sel.read()):
            case conf.WB_sel_t.PC4_OUT:
                self.rf_wd3 = self.pc4
            case conf.WB_sel_t.ALU_OUT:
                self.rf_wd3 = self.buff_mem_wb.alu_out.read()
            case conf.WB_sel_t.SHIFTER_OUT:
                self.rf_wd3 = self.buff_mem_wb.alu_out.read()
            case conf.WB_sel_t.DMEM_OUT:
                self.rf_wd3 = self.buff_mem_wb.dmem_data.read()
            case _:
                self.rf_wd3 = 0

        self.rd = self.buff_mem_wb.rd.read()
        self.reg_wr = bool(self.buff_mem_wb.reg_wr.read())
        self.rf_we3 = self.reg_wr and not bool(self.rst_reg.read())
        
        if self.rf_we3:
            self.rf_inst.write(self.rd, self.rf_wd3)

        self.valid = bool(self.buff_mem_wb.valid.read())