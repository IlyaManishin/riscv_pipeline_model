from pathlib import Path

from .base_tracers import BasePerfTracer
from models.single_cycle.cpu_system import CpuSystem as SC_CpuSystem
from models.pipeline.cpu_system import CpuSystem as PL_CpuSystem


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
            "raw_jumps",     # Total PC redirecting instructions (JAL, JALR, all branches)
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
    def __init__(self, trace_dir: str | Path):
        super().__init__(trace_dir, "performance")
        self.cpu = None
        self.cycles = 0
        self.instructions = 0
        self.stalls = 0
        self.jumps = 0

    def set_cpu(self, cpu: PL_CpuSystem) -> None:
        self.cpu = cpu

    def reset_metrics(self) -> None:
        self.cycles = 0
        self.instructions = 0
        self.stalls = 0
        self.jumps = 0

    def get_header(self) -> list[str]:
        return ["test_name", "cycles", "instructions", "cpi", "stalls", "jumps", "jpi", "status"]

    def format_test_row(self, test_name: str, passed: bool) -> list:
        cpi = round(self.cycles / self.instructions,
                    3) if self.instructions > 0 else 0
        jpi = round(self.jumps / self.instructions,
                    3) if self.instructions > 0 else 0
        status = "PASSED" if passed else "FAILED"
        return [test_name, self.cycles, self.instructions, cpi, self.stalls, self.jumps, jpi, status]

    def trace_cycle(self, cycle: int) -> None:
        if self.cpu is None:
            return

        self.cycles += 1

        core = self.cpu.core
        hdu = core.hdu
        sd = core.stage_decode
        se = core.stage_execute
        sw = core.stage_writeback

        if bool(sw.valid):
            self.instructions += 1

        if hdu.is_id_ex_raw_hazard or hdu.is_id_mem_raw_hazard or hdu.is_id_wb_raw_hazard:
            self.stalls += 1

        if bool(se.jfexe) or bool(sd.jfid):
            self.jumps += 1
