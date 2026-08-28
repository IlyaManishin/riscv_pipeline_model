from dataclasses import dataclass

from sim_base.clock import Clock
from sim_base.mem.register import Register

from risc_v.modules.pc import PC
from risc_v.mem.reg_file import RegFile
from .modules.id import InstructionDecoder
from risc_v.modules.immgen import ImmGen
from risc_v.modules.alu import Alu
from risc_v.modules.shifter import Shifter
from risc_v.modules.br_comparator import BranchComparator
from risc_v.mem.dmem_wr_port import dmem_wr_port
from risc_v.mem.dmem_rd_port import dmem_rd_port

from risc_v.riscv_config import WB_sel
import risc_v.riscv_config as conf


@dataclass
class DMemAccessData:
    addr: int
    wdata: int
    byte_we: int

# =========================================================================
# CORE CLASS DEFINITION (Single-Cycle)
# =========================================================================


class Core:

    # ---------------------------------------------------------------------
    # INITIALIZATION & HARDWARE BINDING
    # ---------------------------------------------------------------------
    def __init__(self, clk: Clock, rst_reg: Register):
        self.clk = clk
        self.rst_reg = rst_reg

        # Hardware instances
        self.pc_inst = PC(rst_reg=rst_reg)
        self.clk.add_trigger(self.pc_inst.reg)

        self.rf_inst = RegFile()
        self.clk.add_trigger(self.rf_inst)

        # Internal Wires (Combinational state of cpu)
        self.pc = 0
        self.instr = None
        self.rd = 0

        self.rf_rd1 = 0
        self.rf_rd2 = 0
        self.rf_wd3 = 0
        self.rf_we3 = False

        self.imm = 0
        self.alu_in_a = 0
        self.alu_in_b = 0
        self.alu_out = 0

        self.shift_shamt = 0
        self.shifter_out = 0
        self.id_controls = None

        # DMEM Interface Wires
        self.dmem_addr = 0
        self.dmem_byte_off = 0
        self.dmem_wdata = 0
        self.dmem_byte_we = 0

    # ---------------------------------------------------------------------
    # STAGE 1: FETCH ADDRESS FROM PC
    # ---------------------------------------------------------------------
    def get_imem_addr(self) -> int:
        return self.pc_inst.read()

    # ---------------------------------------------------------------------
    # STAGE 2: DECODE/REGISTER_FETCH + EXECUTE
    # ---------------------------------------------------------------------
    def dec_exec_alu(self, instr_raw: int) -> DMemAccessData:
        self.instr = conf.Instruction(instr_raw)
        self.pc = self.pc_inst.read()

        # Instruction Decode basic fields
        rs1 = self.instr.rs1
        rs2 = self.instr.rs2
        self.rd = self.instr.rd

        # Register File read (asynchronous / combinational)
        self.rf_rd1 = self.rf_inst.read(rs1)
        self.rf_rd2 = self.rf_inst.read(rs2)

        # Branch Unit & Instruction Decoder
        self.id_controls = InstructionDecoder.decode(
            self.instr)

        # Re-evaluate Branch Unit with exact signedness from decoder
        br_eq, br_lt = BranchComparator.compare(
            self.rf_rd1, self.rf_rd2, bool(self.id_controls.br_un))

        self.id_controls = InstructionDecoder.decode(
            self.instr, br_eq=br_eq, br_lt=br_lt)

        # Immediate Generation
        self.imm = ImmGen.generate(self.instr, self.id_controls.imm_type)

        # DMEM Address Calculation
        self.dmem_addr = (self.rf_rd1 + self.imm) & ((1 << conf.XLEN) - 1)

        # ALU Execution
        self.alu_in_a = self.rf_rd1 if self.id_controls.a_sel else self.pc
        self.alu_in_b = self.rf_rd2 if self.id_controls.b_sel else self.imm
        self.alu_res = Alu.execute(
            self.id_controls.alu_sel, self.alu_in_a, self.alu_in_b)

        # Shifter Execution
        self.shift_shamt = (
            self.rf_rd2 & 0x1F) if self.id_controls.b_sel else self.instr.shamt
        self.shifter_out = Shifter.shift(
            self.rf_rd1, self.shift_shamt, self.id_controls.sh_sel)

        # ALU Out
        self.alu_out = self.shifter_out if self.id_controls.alushift_sel else self.alu_res

        # DMEM Write Port Logic (Data formatting and Byte Enable)
        dmem_we = self.id_controls.dmem_sel.dmem_we
        dmem_funct3 = self.id_controls.dmem_sel.funct3
        self.dmem_byte_off = self.dmem_addr & 0b11

        self.dmem_wdata = 0
        self.dmem_byte_we = 0

        if dmem_we:
            self.dmem_wdata, self.dmem_byte_we = dmem_wr_port(
                self.rf_rd2, self.dmem_byte_off, dmem_funct3)

        return DMemAccessData(
            addr=self.dmem_addr,
            wdata=self.dmem_wdata,
            byte_we=self.dmem_byte_we
        )

    # ---------------------------------------------------------------------
    # STAGE 3: WRITE-BACK (Clock step)
    # ---------------------------------------------------------------------
    def write_back_comb(self, dmem_data_in: int) -> None:
        dmem_funct3 = self.id_controls.dmem_sel.funct3

        # DMEM Read Port Logic (Data formatting from memory)
        dmem_rdata_out = dmem_rd_port(
            dmem_data_in, self.dmem_byte_off, dmem_funct3)

        # Write-back MUX
        match self.id_controls.wb_sel:
            case WB_sel.PC4_OUT:
                self.rf_wd3 = (self.pc + 4) & ((1 << conf.XLEN) - 1)
            case WB_sel.ALU_OUT:
                self.rf_wd3 = self.alu_out
            case WB_sel.DMEM_OUT:
                self.rf_wd3 = dmem_rdata_out
            case _:
                self.rf_wd3 = 0

        # Update Register File
        self.rf_we3 = bool(self.id_controls.reg_wr) and not bool(
            self.rst_reg.read())
        if self.rf_we3:
            self.rf_inst.write(self.rd, self.rf_wd3)

        # Update Program Counter
        br_taken = not bool(self.id_controls.pc_sel)
        self.pc_inst.update_pc(br_taken=br_taken, pc_br=self.alu_out)
