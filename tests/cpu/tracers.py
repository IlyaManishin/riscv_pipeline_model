import csv
from pathlib import Path
from abc import ABC, abstractmethod

from cpu_config import TRACE_ENABLE, TRACE_DIRNAME, REG_COUNT
from risc_v.base.icpu_system import ICpuSystem


# ============================================================
# BASE TRACER CLASS
# ============================================================

class BaseTracer(ABC):
    def __init__(self, tracer_name: str):
        self.tracer_name = tracer_name

    def on_group_start(self, group_name: str) -> None:
        pass

    def on_group_end(self, group_name: str) -> None:
        pass

    def on_test_start(self, test_name: str) -> None:
        pass

    def on_test_end(self, test_name: str, passed: bool) -> None:
        pass

    @abstractmethod
    def trace_cycle(self, cycle: int) -> None:
        pass

# ============================================================
# CSV_TRACER
# ============================================================


class CsvTracer(BaseTracer):
    def __init__(self, tracer_name: str):
        super().__init__(tracer_name)
        self.file = None
        self.writer = None

    @abstractmethod
    def get_header(self) -> list[str]:
        pass

    def on_test_start(self, test_name: str) -> None:
        if TRACE_ENABLE:
            trace_dir = Path(TRACE_DIRNAME) / self.tracer_name
            trace_dir.mkdir(parents=True, exist_ok=True)
            filepath = trace_dir / f"{test_name}.csv"
            self.file = open(filepath, "w", newline="")
            self.writer = csv.writer(self.file)
            self.writer.writerow(self.get_header())

    def write_row(self, row: list) -> None:
        if self.writer is not None:
            self.writer.writerow(row)

    def on_test_end(self, test_name: str, passed: bool) -> None:
        self.close()

    def close(self) -> None:
        if self.file is not None:
            self.file.close()
            self.file = None
            self.writer = None


# ============================================================
# REGISTER_MONITOR_TRACER
# ============================================================

class RegisterTracer(CsvTracer):
    def __init__(self, cpu: ICpuSystem = None, tracer_name: str = "register_trace"):
        super().__init__(tracer_name)
        self.cpu = cpu

    def get_header(self) -> list[str]:
        header = ["cycle", "pc"]
        header.extend(f"x{i}" for i in range(REG_COUNT))
        return header

    def trace_cycle(self, cycle: int) -> None:
        if self.writer is None or self.cpu is None:
            return
        row = [
            cycle,
            self.cpu.get_cur_pc()
        ]
        for i in range(REG_COUNT):
            row.append(self.cpu.reg_file.read(i))
        self.write_row(row)


# ============================================================
# PIPELINE ARCHITECTURE TRACER
# ============================================================

# class PipelineTracer(BaseTracer):
#     def __init__(self, cpu, test_name: str):
#         super().__init__(test_name)
#         self.cpu = cpu

#     def _get_header(self) -> list[str]:
#         header = ["cycle", "pc_wb", "rd_wb", "rf_wb"]
#         header.extend(f"x{i}" for i in range(REG_COUNT))
#         return header

#     def trace_cycle(self, cycle: int) -> None:
#         if self.writer is None:
#             return

#         # Log only on instruction retirement
#         wb_valid = self.cpu.core.wb_stage_valid.read()

#         if wb_valid:
#             wb_pc = self.cpu.core.wb_stage_pc.read()
#             wb_rd = self.cpu.core.wb_stage_rd.read()
#             wb_data = self.cpu.core.wb_stage_data.read()

#             row = [cycle, wb_pc, wb_rd, wb_data]

#             for i in range(REG_COUNT):
#                 row.append(self.cpu.core.rf_inst.read(i))

#             self.writer.writerow(row)
