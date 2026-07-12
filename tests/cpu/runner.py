from pathlib import Path
from typing import Optional
import pytest

from risc_v.base.icpu_system import ICpuSystem
from tracers import BaseTracer
from cpu_config import *
from benchmarks.build_paths import TEST_LIST_NAME


def load_bin_file(filename: str) -> list[int]:
    result = []

    with open(filename, "rb") as f:
        while True:
            chunk = f.read(4)
            if not chunk:
                break
            if len(chunk) < 4:
                chunk = chunk.ljust(4, b'\x00')
            value = int.from_bytes(chunk, byteorder="little")
            result.append(value)

    return result


def load_program(
    cpu: ICpuSystem,
    text_file: str,
    data_file: Optional[str],
) -> None:
    cpu.imem.load_program(load_bin_file(text_file))

    if data_file is not None:
        cpu.dmem.load_data(load_bin_file(data_file))


def execute_program(
    cpu: ICpuSystem,
    tracer: BaseTracer
) -> None:
    try:
        for cycle in range(TIMEOUT_ITERATIONS):
            cpu.step()

            tracer.trace_cycle(cycle)

            rf_dbg = cpu.reg_file.read(RF_DBG_NUM)

            if rf_dbg == CpuTestResult.TEST_RUN.value:
                continue

            if rf_dbg == CpuTestResult.TEST_PASS.value:
                return

            if rf_dbg == CpuTestResult.TEST_FAIL.value:
                pytest.fail("Program returned TEST_FAIL")

            raise ValueError(f"Invalid RF_DBG value: {rf_dbg:#x}")

        pytest.fail(f"Timeout ({TIMEOUT_ITERATIONS} cycles)")

    finally:
        tracer.close()


def run_program(
    cpu: ICpuSystem,
    tracer: BaseTracer,
    text_file: str,
    data_file: Optional[str],
) -> None:
    load_program(cpu, text_file, data_file)
    execute_program(cpu, tracer)


def collect_tests(tests_dir: Path) -> list[tuple[str, Optional[str]]]:
    list_file = tests_dir / TEST_LIST_NAME
    if not list_file.exists():
        raise FileNotFoundError(list_file)

    result: list[tuple[str, Optional[str]]] = []

    with open(list_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split(",")
            imem_path = tests_dir / parts[0].strip()
            
            dmem_path = None
            if len(parts) > 1 and parts[1].strip():
                dmem_path = tests_dir / parts[1].strip()

            if not imem_path.exists():
                raise FileNotFoundError(imem_path)
            if dmem_path and not dmem_path.exists():
                raise FileNotFoundError(dmem_path)

            result.append(
                (
                    str(imem_path),
                    str(dmem_path) if dmem_path is not None else None,
                )
            )

    return result