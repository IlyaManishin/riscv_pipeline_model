import risc_v.riscv_config as conf
from models.pipeline import regs

from risc_v.modules.decode import Instruction_Decoder
from risc_v.modules.immgen import ImmGen
from risc_v.modules.branch_unit import BranchUnit
from risc_v.mem.reg_file import RegFile


class Decode:
    def __init__(self, rf: RegFile, buff_if_id: regs.IF_ID_Stage, buff_id_ex: regs.ID_EX_Stage):
        # --- Dependencies ---
        self.rf_inst: RegFile = rf
        self.buff_if_id: regs.IF_ID_Stage = buff_if_id
        self.buff_id_ex: regs.ID_EX_Stage = buff_id_ex

        # --- Control Signals ---
        self.id_controls = None
        self.instr = None
        self.valid: bool = False
        self.br_eq: bool = False
        self.br_lt: bool = False

        self.jfid: bool = False

        self.jfid_E: bool = False
        self.jfpc_E: int = 0

        # --- Data Path ---
        self.rs1: int = 0
        self.rs2: int = 0
        self.rd: int = 0
        self.rf_rd1: int = 0
        self.rf_rd2: int = 0
        self.pc: int = 0
        self.imm: int = 0
        self.imm_pc: int = 0

    def update(self):
        # ===== ID/EX Pipeline Register: Control-Hazard Signals =====
        # Latch last cycle's combinational jfid/imm_pc into the delayed
        # "_E" copies before recomputing them below. This is exactly the
        # same clocked event as the rest of the ID/EX register further
        # down - it just needs to happen first since jfid/imm_pc are about
        # to be overwritten with this cycle's (new) instruction.
        self.jfid_E = self.jfid
        self.jfpc_E = self.imm_pc

        # ===== Instruction Field Extraction =====
        self.instr = conf.Instruction(self.buff_if_id.instr.read())
        self.pc = self.buff_if_id.pc.read()
        self.valid = bool(self.buff_if_id.valid.read())

        self.rs1 = self.instr.rs1
        self.rs2 = self.instr.rs2
        self.rd = self.instr.rd

        # ===== Register File Read =====
        self.rf_rd1 = self.rf_inst.read(self.rs1)
        self.rf_rd2 = self.rf_inst.read(self.rs2)

        # ===== Control Decode & Branch Resolution =====
        self.id_controls = Instruction_Decoder.decode(self.instr)
        self.br_eq, self.br_lt = BranchUnit.compare(
            self.rf_rd1, self.rf_rd2, bool(self.id_controls.br_un))
        self.id_controls = Instruction_Decoder.decode(
            self.instr, self.br_eq, self.br_lt)

        # ===== Immediate Generation & Branch Target =====
        self.imm = ImmGen.generate(self.instr, self.id_controls.imm_type)
        self.imm_pc = self.pc + self.imm

        # ===== ID/EX Pipeline Register: Data Path =====
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
        self.buff_id_ex.valid.set(self.valid)

        # ===== Control-Hazard Signal (combinational, same cycle) =====
        self.jfid = self.valid and (not bool(self.id_controls.pc_sel)) and (
            not bool(self.id_controls.jf_exe))

    def stall(self):
        self.buff_id_ex.stall()

    def flush(self):
        self.jfid_E = False
        self.jfpc_E = 0
        self.buff_id_ex.flush()
