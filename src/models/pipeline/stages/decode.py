from sim_base.mem.register import Register

import risc_v.riscv_config as conf
from models.pipeline import regs

from risc_v.modules.decode import Instruction_Decoder
from risc_v.modules.immgen import ImmGen
from risc_v.modules.branch_unit import BranchUnit
from risc_v.mem.reg_file import RegFile


class Decode:
    def __init__(self, rf: RegFile, buff_if_id: regs.IF_ID_Stage, buff_id_ex: regs.ID_EX_Stage,
                 jfid_e: Register[bool], jfpc_e: Register[int]):
        ########## INPUT SIGNALS ##########
        self.rf_inst: RegFile = rf
        self.buff_if_id: regs.IF_ID_Stage = buff_if_id

        ########## OUTPUT SIGNALS ##########
        self.buff_id_ex: regs.ID_EX_Stage = buff_id_ex

        # --- jump logic ---
        self.jfid_E: Register[bool] = jfid_e
        self.jfpc_E: Register[int] = jfpc_e
        self.jfid: bool = False
        self.imm_pc: int = 0

        ########## DEBUG SIGNALS ##########
        self.id_controls = None
        self.instr = None
        self.valid: bool = False
        self.br_eq: bool = False
        self.br_lt: bool = False

        self.rs1: int = 0
        self.rs2: int = 0
        self.rd: int = 0
        self.rf_rd1: int = 0
        self.rf_rd2: int = 0
        self.pc: int = 0
        self.imm: int = 0

    def update(self):
        # ===== Instruction Field Extraction =====
        self.instr = conf.Instruction(self.buff_if_id.instr.read())
        self.pc = self.buff_if_id.pc.read()
        self.valid = self.buff_if_id.valid.read()

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

        # ===== Control-Hazard Signal =====
        # id_jfid = valid & !pc_sel & !jf_exe (JALR resolves later, via jfexe_M)
        self.jfid = self.valid and (not bool(self.id_controls.pc_sel)) and (
            not bool(self.id_controls.jf_exe))
        
        if not self.buff_if_id.valid:
            self.flush()
            return 

        # ===== ID/EX Pipeline Register =====
        self.buff_id_ex.write(
            pc=self.pc,
            rf_rd1=self.rf_rd1,
            rf_rd2=self.rf_rd2,
            imm=self.imm,
            rs1=self.instr.rs1,
            rs2=self.instr.rs2,
            rd=self.rd,
            alu_sel=self.id_controls.alu_sel.value,
            a_sel=self.id_controls.a_sel,
            b_sel=self.id_controls.b_sel,
            wb_sel=self.id_controls.wb_sel,
            reg_wr=self.id_controls.reg_wr,
            dmem_sel=self.id_controls.dmem_sel.to_int(),
            jfexe=self.id_controls.jf_exe,
            alushift_sel=self.id_controls.alushift_sel,
            shift_sel=self.id_controls.sh_sel,
            valid=self.valid,
        )

        self.jfid_E.set(self.jfid)
        self.jfpc_E.set(self.imm_pc)

    def stall(self):
        self.jfid_E.set(self.jfid_E.read())
        self.jfpc_E.set(self.jfpc_E.read())
        self.buff_id_ex.stall()

    def flush(self):
        self.jfid_E.set(False)
        self.jfpc_E.set(0)
        self.buff_id_ex.flush()
