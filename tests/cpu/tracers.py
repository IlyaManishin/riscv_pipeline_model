import csv
from pathlib import Path
from abc import ABC, abstractmethod

from cpu_config import TRACE_ENABLE, TRACE_DIRNAME, REG_COUNT

import risc_v.single_cycle.cpu_system as sc_cpu_system


class BaseTracer(ABC):
    def __init__(self, test_name: str):
        self.trace_file = None
        self.writer = None

        if TRACE_ENABLE:
            trace_dir = Path(TRACE_DIRNAME)
            trace_dir.mkdir(parents=True, exist_ok=True)
            filepath = trace_dir / f"{test_name}.csv"

            self.trace_file = open(filepath, "w", newline="")
            self.writer = csv.writer(self.trace_file)
            self.writer.writerow(self._get_header())

    @abstractmethod
    def _get_header(self) -> list[str]:
        pass

    @abstractmethod
    def trace_cycle(self, cycle: int, cpu) -> None:
        pass

    def close(self):
        if self.trace_file is not None:
            self.trace_file.close()


class SingleCycleTracer(BaseTracer):
    def _get_header(self) -> list[str]:
        header = ["cycle", "pc", "rs1", "rs2", "rd"]
        header.extend(f"x{i}" for i in range(REG_COUNT))
        return header

    def trace_cycle(self, cycle: int, cpu: sc_cpu_system.CpuSystem) -> None:
        if self.writer is None:
            return

        row = [
            cycle,
            cpu._core.pc_inst.read(),
            cpu._core.rs1,
            cpu._core.rs2,
            cpu._core.rd,
        ]
        for i in range(REG_COUNT):
            row.append(cpu._core.rf_inst.read(i))

        self.writer.writerow(row)

# class PipelineTracer(BaseTracer):
#     def _get_header(self) -> list[str]:
#         header = ["cycle", "pc_wb", "rd_wb", "rf_wb"]
#         header.extend(f"x{i}" for i in range(REG_COUNT))
#         return header

#     def trace_cycle(self, cycle: int, cpu) -> None:
#         if self.writer is None:
#             return

#         wb_valid = cpu.core.wb_stage_valid.read()

#         if wb_valid:
#             wb_pc = cpu.core.wb_stage_pc.read()
#             wb_rd = cpu.core.wb_stage_rd.read()
#             wb_data = cpu.core.wb_stage_data.read()

#             row = [cycle, wb_pc, wb_rd, wb_data]

#             for i in range(REG_COUNT):
#                 row.append(cpu.core.rf_inst.read(i))

#             self.writer.writerow(row)
