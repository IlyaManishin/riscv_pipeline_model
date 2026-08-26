from typing import Optional
from pathlib import Path
import pytest

from risc_v.base.icpu_system import ICpuSystem
from tracers.base_tracers import BaseTracer
from tests.cpu.tests_config import *
from benches import CpuTestConfig


# ============================================================
# BINARY UTILITIES
# ============================================================

def load_bin_file(file_path: Path) -> list[int]:
    result = []

    with open(file_path, "rb") as f:
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
    text_path: Path,
    data_path: Optional[Path],
) -> None:
    cpu.imem.load_program(load_bin_file(text_path))

    if data_path is not None:
        cpu.dmem.load_data(load_bin_file(data_path))


# ============================================================
# SIMULATION ENGINE
# ============================================================

def execute_program(
    cpu: ICpuSystem,
    tracers: list[BaseTracer],
    max_cycles: int
) -> None:
    try:
        # Main clock cycle loop
        for cycle in range(max_cycles):
            # Run combinational logic
            cpu.step()

            for tracer in tracers:
                tracer.trace_cycle(cycle)

            # Update registers and memory
            cpu.tick()

            # Check test signature
            rf_dbg = cpu.reg_file.read(RF_DBG_NUM)

            if rf_dbg == CpuTestResult.TEST_RUN.value:
                continue

            if rf_dbg == CpuTestResult.TEST_PASS.value:
                return

            if rf_dbg == CpuTestResult.TEST_FAIL.value:
                pytest.fail("Program returned TEST_FAIL")

            raise ValueError(f"Invalid RF_DBG value: {rf_dbg:#x}")

        pytest.fail(f"Timeout ({max_cycles} cycles)")

    finally:
        # Close all tracers appropriately
        for tracer in tracers:
            tracer.close()


def run_program(
    cpu: ICpuSystem,
    tracers: list[BaseTracer],
    test_config: CpuTestConfig
) -> None:
    load_program(cpu, test_config.imem_path, test_config.dmem_path)

    for tracer in tracers:
        tracer.on_test_start(test_config.name)

    passed = False
    try:
        execute_program(cpu, tracers, test_config.max_cycles)
        passed = True
    finally:
        for tracer in tracers:
            tracer.on_test_end(passed)
