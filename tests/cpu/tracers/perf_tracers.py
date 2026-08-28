from pathlib import Path

from .base_tracers import BasePerfTracer
from risc_v import riscv_config as rv_conf

# ========== SYNGLE CYCLE ==========
from models.single_cycle.cpu_system import CpuSystem as SC_CpuSystem

# ============ PIPELINE ============
from models.pipeline.cpu_system import CpuSystem as PL_CpuSystem
from models.pipeline.cpu_core import Core as PL_Core


class SingleCyclePerfTracer(BasePerfTracer):
    # ---------------------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------------------
    def __init__(self, trace_dir: str | Path):
        super().__init__(trace_dir, "performance")
        self.cpu = None
        self.cycles = 0
        self.instructions = 0

        # Branch and jump tracking parameters
        self.raw_jumps = 0
        self.jumps = 0
        self.br = 0
        self.br_taken = 0
        self.jal = 0
        self.jalr = 0

    def set_cpu(self, cpu: SC_CpuSystem) -> None:
        self.cpu = cpu

    def reset_metrics(self) -> None:
        self.cycles = 0
        self.instructions = 0

        # Branch and jump tracking parameters
        self.raw_jumps = 0
        self.jumps = 0
        self.br = 0
        self.br_taken = 0
        self.jal = 0
        self.jalr = 0

    # ---------------------------------------------------------------------
    # REPORT FORMATTING
    # ---------------------------------------------------------------------
    def get_header(self) -> list[str]:
        return [
            "test_name",
            "cycles",        # Total clock cycles
            "instructions",  # Total instructions
            "cpi",           # Cycles per instruction
            "raw_jumps",     # Total PC redirect instructions (JAL, JALR, br)
            "jumps",         # Count of jump operations
            "jpi",           # Jumps per instruction
            "br",            # Total branch instructions encountered
            "br_taken",      # Count of branches taken
            "br_taken%",     # br_taken percent
            "jal",           # Count of JAL instructions
            "jalr",          # Count of JALR instructions
            "status"         # Test result status (PASSED/FAILED)
        ]

    def format_test_row(self, test_name: str, passed: bool) -> list:
        cpi = round(self.cycles / self.instructions,
                    3) if self.instructions > 0 else 0
        jpi = round(self.jumps / self.instructions,
                    3) if self.instructions > 0 else 0
        br_taken_pct = round((self.br_taken / self.br) * 100,
                             1) if self.br > 0 else 0.0
        status = "PASSED" if passed else "FAILED"

        return [
            test_name, self.cycles, self.instructions, cpi,
            self.raw_jumps, self.jumps, jpi, self.br, self.br_taken,  f"{br_taken_pct}%",
            self.jal, self.jalr, status
        ]

    # ---------------------------------------------------------------------
    # CYCLE EXECUTION TRACING
    # ---------------------------------------------------------------------
    def trace_cycle(self, cycle: int) -> None:
        if self.cpu is None:
            return

        self.cycles += 1
        core = self.cpu._core

        if bool(core.rst_reg.read()):
            return

        self.instructions += 1

        # pc_sel == 0 indicates a control transfer (jump or taken branch)
        pc_sel = bool(core.id_controls.pc_sel)

        if not pc_sel:
            self.jumps += 1

        shifted_opcode = core.instr.opcode >> 2

        # Check for specific instruction types based on raw opcode
        if shifted_opcode == 0b11000:       # Branch
            self.raw_jumps += 1
            self.br += 1
            if not pc_sel:
                self.br_taken += 1

        elif shifted_opcode == 0b11011:     # JAL
            self.raw_jumps += 1
            self.jal += 1

        elif shifted_opcode == 0b11001:     # JALR
            self.raw_jumps += 1
            self.jalr += 1


class PipelinePerfTracer(BasePerfTracer):
    # ---------------------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------------------
    def __init__(self, trace_dir: str | Path):
        super().__init__(trace_dir, "performance")
        self.cpu = None
        self.cycles = 0
        self.instructions = 0

        # Hazard and jump tracking parameters
        self.stalls = 0
        self.jumps = 0
        self.jfid_hazards = 0
        self.jfexe_hazards = 0
        self.ex_raw_hazards = 0
        self.mem_raw_hazards = 0
        self.wb_raw_hazards = 0

    def set_cpu(self, cpu: PL_CpuSystem) -> None:
        self.cpu = cpu

    def reset_metrics(self) -> None:
        self.cycles = 0
        self.instructions = 0

        # Hazard and jump tracking parameters
        self.stalls = 0
        self.jumps = 0
        self.jfid_hazards = 0
        self.jfexe_hazards = 0
        self.ex_raw_hazards = 0
        self.mem_raw_hazards = 0
        self.wb_raw_hazards = 0
        self.no_fwd_hazards = 0

    # ---------------------------------------------------------------------
    # REPORT FORMATTING
    # ---------------------------------------------------------------------
    def get_header(self) -> list[str]:
        return [
            "test_name",
            "cycles",
            "instructions",      # Total instructions executed
            "cpi",               # Cycles per instruction
            "jumps",             # Count of jump/branch control transfers
            "jpi",               # Jumps per instruction
            "jfid_hazards",      # Count of control hazards in Decode stage
            "jfexe_hazards",     # Count of control hazards in Execute stage
            "stalls",            # Total cycles lost to stalls (RAW hazards)
            "ex_raw_hazards",    # Count of RAW hazards against EX stage
            "mem_raw_hazards",   # Count of RAW hazards against MEM stage
            "wb_raw_hazards",    # Count of RAW hazards against WB stage
            "no_fwd_hazards",    # Count of RAW hazards which cannot be forwarded without stalls
            "status"             # Test result status (PASSED/FAILED)
        ]

    def format_test_row(self, test_name: str, passed: bool) -> list:
        cpi = round(self.cycles / self.instructions,
                    3) if self.instructions > 0 else 0
        jpi = round(self.jumps / self.instructions,
                    3) if self.instructions > 0 else 0
        status = "PASSED" if passed else "FAILED"

        return [
            test_name, self.cycles, self.instructions, cpi,
            self.jumps, jpi,
            self.jfid_hazards, self.jfexe_hazards,
            self.stalls, self.ex_raw_hazards, self.mem_raw_hazards, self.wb_raw_hazards,
            self.no_fwd_hazards,
            status
        ]

    # ---------------------------------------------------------------------
    # CYCLE EXECUTION TRACING
    # ---------------------------------------------------------------------
    def trace_cycle(self, cycle: int) -> None:
        if self.cpu is None:
            return

        self.cycles += 1

        core = self.cpu.core
        stage_wb = core.stage_writeback

        if bool(stage_wb.valid):
            self.instructions += 1

        self.trace_hazards(core)

    # ---------------------------------------------------------------------
    # HAZARD & CONTROL TRACING
    # ---------------------------------------------------------------------
    def trace_hazards(self, core: PL_Core) -> None:
        """Trace RAW data hazards and control hazards with strict priority logic."""
        hdu = core.hdu

        # ===== Control Hazards (Priority: jfexe > jfid) =====
        if hdu.jfexe_hazard:
            self.jfexe_hazards += 1
            self.jumps += 1
            return
        elif hdu.jfid_hazard:
            self.jfid_hazards += 1
            self.jumps += 1
            return

        # ===== RAW Data Hazards =====
        if hdu.raw_hazard:
            self.stalls += 1

        if hdu.id_ex_raw_hazard:
            self.ex_raw_hazards += 1

        if hdu.id_mem_raw_hazard:
            self.mem_raw_hazards += 1

        if hdu.id_wb_raw_hazard:
            self.wb_raw_hazards += 1

        if self.is_no_fwd_hazard(core):
            self.no_fwd_hazards += 1

    def is_no_fwd_hazard(self, core: PL_Core) -> bool:
        hdu = core.hdu
        buff_id_ex = core.buff_id_ex
        buff_ex_mem = core.buff_ex_mem

        if not hdu.raw_hazard:
            return False

        id_controls_out_E = buff_id_ex.id_controls
        ex_wb_sel = id_controls_out_E.read().wb_sel
        ex_dmem_load = (ex_wb_sel == rv_conf.WB_sel.DMEM_OUT)
        if hdu.id_ex_raw_hazard and ex_dmem_load:
            return True

        mem_wb_sel = buff_ex_mem.wb_sel.read()
        mem_dmem_load = (mem_wb_sel == rv_conf.WB_sel.DMEM_OUT)
        if hdu.id_mem_raw_hazard and mem_dmem_load:
            return True
        
        return False
