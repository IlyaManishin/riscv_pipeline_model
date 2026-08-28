import risc_v.riscv_config as conf
from models.pipeline import regs
from models.pipeline.modules.id import InstructionDecoder

from risc_v.modules.immgen import ImmGen
from risc_v.mem.reg_file import RegFile


class Decode:
    def __init__(self, rf: RegFile, buff_if_id: regs.IF_ID_Stage, buff_id_ex: regs.ID_EX_Stage):
        ########## INPUT SIGNALS ##########
        self.rf_inst: RegFile = rf
        self.buff_if_id: regs.IF_ID_Stage = buff_if_id

        ########## OUTPUT SIGNALS ##########
        self.buff_id_ex: regs.ID_EX_Stage = buff_id_ex

        ########## DEBUG SIGNALS ##########
        self.id_controls = None
        self.instr = None
        self.valid: bool = False

        self.rs1: int = 0
        self.rs2: int = 0
        self.rd: int = 0
        self.rf_rd1: int = 0
        self.rf_rd2: int = 0
        self.pc: int = 0
        self.imm: int = 0

        self.is_stall: bool = False
        self.is_flush: bool = False

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

        # ===== Control Decode =====
        self.id_controls = InstructionDecoder.decode(self.instr)

        # ===== Immediate Generation =====
        self.imm = ImmGen.generate(self.instr, self.id_controls.imm_type)

        if not self.buff_if_id.valid.read(): # maybe not necessary because there is no flush in fetch (reset?)
            self.flush()
            return

        # ===== ID/EX Pipeline Register =====
        self.buff_id_ex.pc.set(self.pc)
        self.buff_id_ex.rf_rd1.set(self.rf_rd1)
        self.buff_id_ex.rf_rd2.set(self.rf_rd2)
        self.buff_id_ex.imm.set(self.imm)
        self.buff_id_ex.rs1.set(self.instr.rs1)
        self.buff_id_ex.rs2.set(self.instr.rs2)
        self.buff_id_ex.rd.set(self.rd)
        self.buff_id_ex.funct3.set(self.instr.funct3)
        self.buff_id_ex.alu_sel.set(self.id_controls.alu_sel.value)
        self.buff_id_ex.a_sel.set(self.id_controls.a_sel)
        self.buff_id_ex.b_sel.set(self.id_controls.b_sel)
        self.buff_id_ex.wb_sel.set(self.id_controls.wb_sel)
        self.buff_id_ex.reg_wr.set(self.id_controls.reg_wr)
        self.buff_id_ex.dmem_sel.set(self.id_controls.dmem_sel)
        self.buff_id_ex.pc_sel.set(self.id_controls.pc_sel)
        self.buff_id_ex.br_unit_sel.set(bool(self.id_controls.br_unit_sel))
        self.buff_id_ex.br_un.set(bool(self.id_controls.br_un))
        self.buff_id_ex.alushift_sel.set(bool(self.id_controls.alushift_sel))
        self.buff_id_ex.shift_sel.set(self.id_controls.sh_sel)
        self.buff_id_ex.valid.set(self.valid)

        self.is_stall = False
        self.is_flush = False

    def stall(self):
        # flush has higher priority
        if self.is_flush:
            return

        self.buff_id_ex.stall()

        self.is_stall = True

    def flush(self):
        self.buff_id_ex.flush()

        self.is_flush = False

    def rst(self):
        self.flush()