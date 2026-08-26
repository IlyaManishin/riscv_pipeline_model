from sim_base.mem.register import Register

from risc_v.mem.reg_file import RegFile
from risc_v.mem.dmem_rd_port import dmem_rd_port
import risc_v.riscv_config as conf

from models.pipeline import regs


class WriteBack:
    def __init__(self, rf: RegFile, buff_mem_wb: regs.MEM_WB_Stage, rst_reg: Register[bool]):
        ########## INPUT SIGNALS ##########
        self.buff_mem_wb: regs.MEM_WB_Stage = buff_mem_wb
        self.rst_reg: Register = rst_reg

        ########## OUTPUT SIGNALS ##########
        self.rf_inst: RegFile = rf

        ########## DEBUG SIGNALS ##########
        self.valid: bool = False

        self.rf_we3: bool = False
        self.reg_wr: bool = False
        self.dmem_rdata: int = 0

        self.rf_wd3: int = 0
        self.rd: int = 0
        self.pc4: int = 0

    def update(self):
        # ===== Data Memory Read Port =====
        # dmem's address was staged by Memory last cycle, so the raw word
        # (and the byte/funct3 extraction) is only available now.
        self.dmem_rdata = dmem_rd_port(
            self.buff_mem_wb.dmem_data.read(),
            self.buff_mem_wb.dmem_byte_off.read(),
            self.buff_mem_wb.dmem_funct3.read(),
        )

        # ===== Write-Back Data Multiplexing =====
        self.pc4 = self.buff_mem_wb.pc4.read()
        wb_sel = self.buff_mem_wb.wb_sel.read()
        match wb_sel:
            case conf.WB_sel.PC4_OUT:
                self.rf_wd3 = self.pc4
            case conf.WB_sel.ALU_OUT:
                self.rf_wd3 = self.buff_mem_wb.alu_out.read()
            case conf.WB_sel.DMEM_OUT:
                self.rf_wd3 = self.dmem_rdata
            case _:
                self.rf_wd3 = 0

        # ===== Register File Write =====
        self.rd = self.buff_mem_wb.rd.read()
        self.rf_we3 = self.buff_mem_wb.reg_wr.read()

        if self.rf_we3:
            self.rf_inst.write(self.rd, self.rf_wd3)

        self.valid = self.buff_mem_wb.valid.read()
