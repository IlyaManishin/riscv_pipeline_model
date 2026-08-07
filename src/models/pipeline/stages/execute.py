from sim_base.mem.register import Register

from models.pipeline import regs

from risc_v.modules.alu import Alu
from risc_v.modules.shifter import Shifter
from risc_v.riscv_config import Alu_sel_t, Shift_sel_t


class Execute:
    def __init__(self, buff_id_ex: regs.ID_EX_Stage, buff_ex_mem: regs.EX_MEM_Stage,
                 jfexe_M: Register[bool], jfpc_M: Register[int]):
        ########## INPUT SIGNALS ##########
        self.buff_id_ex: regs.ID_EX_Stage = buff_id_ex

        ########## OUTPUT SIGNALS ##########
        self.buff_ex_mem: regs.EX_MEM_Stage = buff_ex_mem

        # --- jump logic ---
        self.jfexe_M: Register[bool] = jfexe_M
        self.jfpc_M: Register[int] = jfpc_M
        self.jfexe: bool = False
        self.jfpc: int = 0

        ########## DEBUG SIGNALS ##########
        self.reg_wr: bool = False
        self.valid: bool = False

        self.rd1: int = 0
        self.rd2: int = 0
        self.alu_in_a: int = 0
        self.alu_in_b: int = 0
        self.shift_shamt: int = 0
        self.alures: int = 0
        self.shift_res: int = 0
        self.rd: int = 0
        self.pc4: int = 0

    def update(self):
        # ===== Operand Read =====
        self.rd1 = self.buff_id_ex.rf_rd1.read()
        self.rd2 = self.buff_id_ex.rf_rd2.read()
        self.valid = self.buff_id_ex.valid.read()

        # ===== ALU Operand Multiplexing =====
        self.alu_in_a = self.rd1 if self.buff_id_ex.a_sel.read() else self.buff_id_ex.pc.read()
        self.alu_in_b = self.rd2 if self.buff_id_ex.b_sel.read() else self.buff_id_ex.imm.read()

        # ===== Arithmetic / Logic =====
        self.alures = Alu.execute(Alu_sel_t(self.buff_id_ex.alu_sel.read()),
                                  self.alu_in_a, self.alu_in_b)

        # ===== Shifter =====
        self.shift_shamt = (self.rd2 & 0x1F) if self.buff_id_ex.b_sel.read() else (
            self.buff_id_ex.rs2.read() & 0x1F)
        self.shift_res = Shifter.shift(sel=Shift_sel_t(self.buff_id_ex.shift_sel.read()),
                                   data=self.alu_in_a,
                                   shamt=self.shift_shamt)

        self.rd = self.buff_id_ex.rd.read()
        self.reg_wr = self.buff_id_ex.reg_wr.read()
        self.pc4 = self.buff_id_ex.pc.read() + 4

        # ===== EX/MEM Pipeline Register =====
        self.buff_ex_mem.write(
            alu_out=self.shift_res if self.buff_id_ex.alushift_sel.read() else self.alures,
            rf_rd2=self.rd2,
            rd=self.rd,
            wb_sel=self.buff_id_ex.wb_sel.read(),
            reg_wr=self.reg_wr,
            dmem_sel=self.buff_id_ex.dmem_sel.read(),
            pc4=self.pc4,
            valid=self.valid
        )

        # ===== Control-Hazard Signal =====
        # ex_jfexe = valid & jf_exe; target is the raw ALU result (rd1 + imm)
        self.jfexe = self.valid and self.buff_id_ex.jfexe.read()
        self.jfpc = self.alures

        self.jfexe_M.set(self.jfexe)
        self.jfpc_M.set(self.jfpc)
