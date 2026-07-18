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
        if not bool(core.rst_reg.read()):
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
        self.flushes = 0

    def set_cpu(self, cpu: PL_CpuSystem) -> None:
        self.cpu = cpu

    def reset_metrics(self) -> None:
        self.cycles = 0
        self.instructions = 0
        self.stalls = 0
        self.flushes = 0

    def get_header(self) -> list[str]:
        return ["test_name", "cycles", "instructions", "cpi", "stalls", "flushes", "status"]

    def format_test_row(self, test_name: str, passed: bool) -> list:
        cpi = round(self.cycles / self.instructions, 3) if self.instructions > 0 else 0
        status = "PASSED" if passed else "FAILED"
        return [test_name, self.cycles, self.instructions, cpi, self.stalls, self.flushes, status]

    def trace_cycle(self, cycle: int) -> None:
        if self.cpu is None:
            return
        
        self.cycles += 1
        
        sd = self.cpu.stage_decode
        se = self.cpu.stage_execute
        sm = self.cpu.stage_memory
        sw = self.cpu.stage_writeback

        if bool(sw.valid):
            self.instructions += 1

        decode_jf_exe = bool(sd.id_controls.jf_exe) if sd.id_controls is not None else False
        
        raw_ex = bool(se.reg_wr and se.rd != 0 and (se.rd == sd.rs1 or se.rd == sd.rs2))
        raw_mem = bool(sm.reg_wr and sm.rd != 0 and (sm.rd == sd.rs1 or sm.rd == sd.rs2))
        raw_wb = bool(sw.reg_wr and sw.rd != 0 and (sw.rd == sd.rs1 or sw.rd == sd.rs2))

        if decode_jf_exe or raw_ex or raw_mem or raw_wb:
            self.stalls += 1

        if decode_jf_exe or bool(se.jfexe) or bool(sd.jfid) or raw_ex or raw_mem or raw_wb:
            self.flushes += 1