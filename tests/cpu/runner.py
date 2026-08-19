from typing import Optional
import pytest

from risc_v.base.icpu_system import ICpuSystem
from tracers.base_tracers import BaseTracer
from tests.cpu.tests_config import *


# ============================================================
# BINARY UTILITIES
# ============================================================

def load_bin_file(filename: str) -> list[int]:
    result = []

    with open(filename, "rb") as f:
        while True:
            chunk = f.read(4)
            if not chunk:
                break
            # Pad to 32-bit alignment
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


# ============================================================
# SIMULATION ENGINE
# ============================================================

def execute_program(
    cpu: ICpuSystem,
    tracers: list[BaseTracer]
) -> None:
    try:
        # Main clock cycle loop
        for cycle in range(TIMEOUT_ITERATIONS):
            cpu.step()

            for tracer in tracers:
                tracer.trace_cycle(cycle)

            # Check test signature
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
    tracers: list[BaseTracer],
    test_name: str,
    text_file: str,
    data_file: Optional[str],
) -> None:
    load_program(cpu, text_file, data_file)

    for tracer in tracers:
        tracer.on_test_start(test_name)

    passed = False
    try:
        execute_program(cpu, tracers)
        passed = True
    finally:
        for tracer in tracers:
            tracer.on_test_end(passed)
