import csv
from pathlib import Path
from abc import ABC, abstractmethod

from tests_config import TRACE_ENABLE


# ============================================================
# BASE_TRACER
# ============================================================

class BaseTracer(ABC):
    def __init__(self, trace_dir: str | Path, tracer_name: str):
        self.tracer_name = tracer_name
        self.trace_dir = trace_dir

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
    def __init__(self, trace_dir: str | Path, tracer_name: str):
        super().__init__(trace_dir, tracer_name)
        self.file = None
        self.writer = None

    @abstractmethod
    def get_header(self) -> list[str]:
        pass

    def on_test_start(self, test_name: str) -> None:
        if TRACE_ENABLE:
            trace_dir = Path(self.trace_dir) / test_name
            trace_dir.mkdir(parents=True, exist_ok=True)

            filepath = trace_dir / f"{self.tracer_name}.csv"
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
