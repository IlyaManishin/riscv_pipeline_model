import csv
from pathlib import Path
from abc import ABC, abstractmethod

from tests_config import BASE_TRACE_ENABLE, PERF_SUMMARY_NAME


# ============================================================
# BASE_TRACER
# ============================================================

class BaseTracer(ABC):
    def __init__(self, trace_dir: str | Path, tracer_name: str):
        self.tracer_name = tracer_name
        self.trace_dir = trace_dir

    def on_test_start(self, test_name: str) -> None:
        pass

    def on_test_end(self, passed: bool) -> None:
        pass

    def trace_cycle(self, cycle: int) -> None:
        pass

    def _is_trace(self) -> bool:
        return BASE_TRACE_ENABLE


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
        if not self._is_trace():
            return

        test_trace_dir = Path(self.trace_dir) / test_name
        test_trace_dir.mkdir(parents=True, exist_ok=True)

        filepath = test_trace_dir / f"{test_name}.csv"
        self.file = open(filepath, "w", newline="")

        self.writer = csv.writer(self.file)
        self.writer.writerow(self.get_header())

    def write_row(self, row: list) -> None:
        if self.writer is not None:
            self.writer.writerow(row)

    def on_test_end(self, passed: bool) -> None:
        self.close()

    def close(self) -> None:
        if self.file is not None:
            self.file.close()
            self.file = None
            self.writer = None


# ============================================================
# CPU_PERFORMANCE_TRACER
# ============================================================

class BasePerfTracer(BaseTracer):
    def __init__(self, trace_dir: str | Path, tracer_name: str):
        super().__init__(trace_dir, tracer_name)
        self.file = None
        self.writer = None
        self.current_test_name = None
        self.current_group_name = None

        self.summary_path = Path(trace_dir) / PERF_SUMMARY_NAME
        if self.summary_path.exists():
            self.summary_path.unlink()

    @abstractmethod
    def get_header(self) -> list[str]:
        pass

    @abstractmethod
    def format_test_row(self, test_name: str, passed: bool) -> list:
        pass

    @abstractmethod
    def reset_metrics(self) -> None:
        pass

    def on_group_start(self, group_name: str) -> None:
        if not self._is_trace():
            return
        self.current_group_name = group_name
        group_dir = Path(self.trace_dir)
        group_dir.mkdir(parents=True, exist_ok=True)
        filepath = group_dir / f"{group_name}_{self.tracer_name}.csv"
        self.file = open(filepath, "w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file)
        self.writer.writerow(self.get_header())

    def on_group_end(self) -> None:
        if self.file is not None:
            self.file.close()
            self.file = None
            self.writer = None
        self.current_group_name = None

    def on_test_start(self, test_name: str) -> None:
        self.current_test_name = test_name
        self.reset_metrics()

    def on_test_end(self, passed: bool) -> None:
        if self.writer is not None and self.current_test_name is not None:
            row = self.format_test_row(self.current_test_name, passed)
            self.writer.writerow(row)
            summary_exists = self.summary_path.exists()
            with open(self.summary_path, "a", newline="", encoding="utf-8") as f:
                s_writer = csv.writer(f)
                if not summary_exists:
                    s_writer.writerow(["group"] + self.get_header())
                s_writer.writerow([self.current_group_name] + row)

        self.current_test_name = None

    def close(self) -> None:
        pass