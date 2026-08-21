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
        self.valid: bool = False

        self.alu_out: int = 0
        self.pc4: int = 0

        self.is_stall: bool = False
        self.is_flush: bool = False

    def update(self):
        # ===== Operand Read =====
        rd1 = self.buff_id_ex.rf_rd1.read()
        rd2 = self.buff_id_ex.rf_rd2.read()
        
        self.valid = self.buff_id_ex.valid.read()

        # ===== ALU Operand Multiplexing =====
        alu_in_a = rd1 if self.buff_id_ex.a_sel.read() else self.buff_id_ex.pc.read()
        alu_in_b = rd2 if self.buff_id_ex.b_sel.read() else self.buff_id_ex.imm.read()

        # ===== Arithmetic / Logic =====
        alures = Alu.execute(Alu_sel_t(self.buff_id_ex.alu_sel.read()),
                             alu_in_a, alu_in_b)

        # ===== Shifter =====
        shift_shamt = (rd2 & 0x1F) if self.buff_id_ex.b_sel.read() else (
            self.buff_id_ex.rs2.read() & 0x1F)
        shift_res = Shifter.shift(sel=Shift_sel_t(self.buff_id_ex.shift_sel.read()),
                                  data=alu_in_a,
                                  shamt=shift_shamt)

        self.pc4 = self.buff_id_ex.pc.read() + 4

        # ===== ALU out =====
        self.alu_out = shift_res if self.buff_id_ex.alushift_sel.read() else alures

        # ===== EX/MEM Pipeline Register =====
        self.buff_ex_mem.alu_out.set(self.alu_out)
        self.buff_ex_mem.rf_rd2.set(rd2)
        self.buff_ex_mem.rd.set(self.buff_id_ex.rd.read())
        self.buff_ex_mem.wb_sel.set(self.buff_id_ex.wb_sel.read())
        self.buff_ex_mem.reg_wr.set(self.buff_id_ex.reg_wr.read())
        self.buff_ex_mem.dmem_sel.set(self.buff_id_ex.dmem_sel.read())
        self.buff_ex_mem.pc4.set(self.pc4)
        self.buff_ex_mem.valid.set(self.valid)

        # ===== Control-Hazard Signal =====
        self.jfexe = bool(self.valid and self.buff_id_ex.jfexe.read())
        self.jfpc = self.alu_out

        self.jfexe_M.set(self.jfexe)
        self.jfpc_M.set(self.jfpc)

        self.is_stall = False
        self.is_flush = False

    def stall(self):
        # flush has higher priority
        if self.is_flush:
            return

        self.buff_ex_mem.stall()
        self.is_stall = True

    def flush(self):
        self.buff_ex_mem.flush()
        self.jfexe_M.set(False)
        self.jfpc_M.set(0)
        
        self.is_flush = True

    def rst(self):
        self.flush()