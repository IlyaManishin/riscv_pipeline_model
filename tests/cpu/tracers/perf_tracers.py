from pathlib import Path

from .base_tracers import BasePerfTracer
from risc_v.single_cycle.cpu_system import CpuSystem as SC_CpuSystem
from risc_v.pipeline.cpu_system import CpuSystem as PL_CpuSystem


class SingleCyclePerfTracer(BasePerfTracer):
    def __init__(self, trace_dir: str | Path):
        super().__init__(trace_dir, "performance")
        self.cpu = None
        self.cycles = 0
        self.instructions = 0
        self.jumps = 0

    def set_cpu(self, cpu: SC_CpuSystem) -> None:
        self.cpu = cpu

    def reset_metrics(self) -> None:
        self.cycles = 0
        self.instructions = 0
        self.jumps = 0

    def get_header(self) -> list[str]:
        return ["test_name", "cycles", "instructions", "cpi", "jumps", "jpi", "status"]

    def format_test_row(self, test_name: str, passed: bool) -> list:
        cpi = round(self.cycles / self.instructions,
                    3) if self.instructions > 0 else 0
        jpi = round(self.jumps / self.instructions,
                    3) if self.instructions > 0 else 0
        status = "PASSED" if passed else "FAILED"
        return [test_name, self.cycles, self.instructions, cpi, self.jumps, jpi, status]

    def trace_cycle(self, cycle: int) -> None:
        if self.cpu is None:
            return
        self.cycles += 1
        core = self.cpu._core

        if bool(core.rst_reg.read()):
            return

        self.instructions += 1
        if not bool(core.id_controls.pc_sel):
            self.jumps += 1


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