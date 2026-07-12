from pathlib import Path
from typing import Optional
import pytest
import csv

from risc_v.single_cycle import cpu_system
from bench_builder.build_paths import BUILD_DIR, ASM_DIRNAME, TEST_LIST_NAME
from cpu_config import *


def load_hex_file(filename: str) -> list[int]:
    result = []

    with open(filename, "r") as f:
        for line_num, line in enumerate(f, 1):
            clean_line = line.strip().replace("0x", "").replace("0X", "").replace(" ", "")

            if not clean_line:
                continue

            try:
                value = int(clean_line, 16)
            except ValueError as e:
                raise ValueError(
                    f"Invalid hex at line {line_num}: '{clean_line}'"
                ) from e

            if value > (1 << XLEN) - 1:
                raise ValueError(
                    f"Value 0x{value:X} exceeds {XLEN} bits at line {line_num}"
                )

            result.append(value)

    return result


def load_program(
    cpu: cpu_system.CpuSystem,
    text_file: str,
    data_file: Optional[str],
) -> None:
    cpu.imem.load_program(load_hex_file(text_file))

    if data_file is not None:
        cpu.dmem.load_data(load_hex_file(data_file))


def execute_program(
    cpu: cpu_system.CpuSystem,
    text_file: str
) -> None:
    trace_file, trace = create_trace_writer(text_file)

    try:
        for cycle in range(TIMEOUT_ITERATIONS):
            cpu.step()

            if trace is not None:
                row = [
                    cycle,
                    cpu.core.pc_inst.read(),
                    cpu.core.rs1,
                    cpu.core.rs2,
                    cpu.core.rd,
                ]
                for i in range(REG_COUNT):
                    row.append(cpu.core.rf_inst.read(i))
                trace.writerow(row)

            rf_dbg = cpu.core.rf_inst.read(RF_DBG_NUM)

            if rf_dbg == CpuTestResult.TEST_RUN.value:
                continue

            if rf_dbg == CpuTestResult.TEST_PASS.value:
                return

            if rf_dbg == CpuTestResult.TEST_FAIL.value:
                pytest.fail("Program returned TEST_FAIL")

            raise ValueError(f"Invalid RF_DBG value: {rf_dbg:#x}")

        pytest.fail(f"Timeout ({TIMEOUT_ITERATIONS} cycles)")

    finally:
        if trace_file is not None:
            trace_file.close()


def create_trace_writer(text_file: str):
    if not TRACE_ENABLE:
        return None, None

    trace_dir = Path(TRACE_DIRNAME)
    trace_dir.mkdir(parents=True, exist_ok=True)

    trace_file = trace_dir / (Path(text_file).stem + ".csv")

    f = open(trace_file, "w", newline="")
    writer = csv.writer(f)

    header = ["cycle", "pc", "rs1", "rs2", "rd"]
    header.extend(f"x{i}" for i in range(REG_COUNT))

    writer.writerow(header)

    return f, writer


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

            text_path = tests_dir / line
            data_path = text_path.parent / f"{text_path.stem}_data.hex" # add in rars_convert_to_hex

            result.append(
                (
                    str(text_path),
                    str(data_path) if data_path.exists() else None,
                )
            )

    return result


@pytest.fixture
def cpu() -> cpu_system.CpuSystem:
    return cpu_system.CpuSystem()


def run_program(
    cpu: cpu_system.CpuSystem,
    text_file: str,
    data_file: Optional[str],
) -> None:
    load_program(cpu, text_file, data_file)
    execute_program(cpu, text_file)

@pytest.mark.parametrize(
    "text_file, data_file",
    collect_tests(BUILD_DIR / ASM_DIRNAME),
)
def test_program(
    cpu: cpu_system.CpuSystem,
    text_file: str,
    data_file: Optional[str],
) -> None:
    run_program(cpu, text_file, data_file)
