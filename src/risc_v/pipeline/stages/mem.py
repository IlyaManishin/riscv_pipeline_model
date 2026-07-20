import risc_v.riscv_config as conf
import risc_v.pipeline.regs as regs

from risc_v.modules.mem.dmem import DataMem
from risc_v.modules.dmem_wr_port import dmem_wr_port
from risc_v.modules.dmem_rd_port import dmem_rd_port


import risc_v.riscv_config as conf
import risc_v.pipeline.regs as regs
from risc_v.modules.mem.dmem import DataMem
from risc_v.modules.dmem_wr_port import dmem_wr_port
from risc_v.modules.dmem_rd_port import dmem_rd_port


class Memory:
    def __init__(self, dmem: DataMem, buff_ex_mem: regs.EX_MEM_Stage, buff_mem_wb: regs.MEM_WB_Stage):
        # --- Dependencies ---
        self.dmem: DataMem = dmem
        self.buff_ex_mem: regs.EX_MEM_Stage = buff_ex_mem
        self.buff_mem_wb: regs.MEM_WB_Stage = buff_mem_wb

        # --- Control Signals ---
        self.dmem_sel: conf.DMem_sel = conf.DMem_sel.NONE
        self.dmem_we: bool = False
        self.valid: bool = False
        self.reg_wr: bool = False

        # --- Data Path ---
        self.dmem_addr: int = 0
        self.dmem_funct3: int = 0
        self.dmem_byte_off: int = 0
        self.dmem_wdata: int = 0
        self.dmem_byte_we: int = 0
        self.dmem_rdata: int = 0
        self.pc4: int = 0
        self.rd: int = 0

    def update(self):
        self.dmem_addr = self.buff_ex_mem.alu_out.read()

        self.dmem_sel = conf.DMem_sel.from_int(
            self.buff_ex_mem.dmem_sel.read())
        self.dmem_we = self.dmem_sel.is_write()
        self.dmem_funct3 = self.dmem_sel.funct3()
        self.dmem_byte_off = self.dmem_addr & 0b11

        self.dmem_wdata = 0
        self.dmem_byte_we = 0

        if self.dmem_we:
            self.dmem_wdata, self.dmem_byte_we = dmem_wr_port(
                self.buff_ex_mem.rf_rd2.read(), self.dmem_byte_off, self.dmem_funct3)

        word_dmem_addr = (self.dmem_addr & 0x0FFFFFFF) >> 2

        if self.dmem_byte_we != 0:
            self.dmem.write(word_dmem_addr, self.dmem_wdata,
                            byte_we=self.dmem_byte_we)

        data_to_cpu = self.dmem.read(word_dmem_addr)

        self.dmem_rdata = dmem_rd_port(
            data_to_cpu, self.dmem_byte_off, self.dmem_funct3)

        self.buff_mem_wb.alu_out.set(self.buff_ex_mem.alu_out.read())
        self.buff_mem_wb.dmem_data.set(self.dmem_rdata)
        self.rd = self.buff_ex_mem.rd.read()
        self.buff_mem_wb.rd.set(self.rd)
        self.buff_mem_wb.wb_sel.set(self.buff_ex_mem.wb_sel.read())
        self.reg_wr = bool(self.buff_ex_mem.reg_wr.read())
        self.buff_mem_wb.reg_wr.set(self.reg_wr)
        self.pc4 = self.buff_ex_mem.pc4.read()
        self.buff_mem_wb.pc4.set(self.pc4)

        self.valid = bool(self.buff_ex_mem.valid.read())
        self.buff_mem_wb.valid.set(self.valid)
