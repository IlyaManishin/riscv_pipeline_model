from pathlib import Path
from typing import Optional

import pytest

from risc_v.single_cycle import cpu_system
import config_tests as confs


TEST_DIR = Path(confs.TEST_DIR)
LIST_FILE = TEST_DIR / "ub.lst"


def load_hex_file(filename: str) -> list[int]:
    result = []

    with open(filename, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            if not line:
                continue

            line = line.replace("0x", "").replace("0X", "").replace(" ", "")

            if not line:
                continue

            try:
                value = int(line, 16)
            except ValueError as e:
                raise ValueError(
                    f"Invalid hex at line {line_num}: '{line}'"
                ) from e

            if value > 0xFFFFFFFF:
                raise ValueError(
                    f"Value 0x{value:X} exceeds 32 bits at line {line_num}"
                )

            result.append(value)

    return result


def run_program(
    cpu: cpu_system.CpuSystem,
    text_file: str,
    data_file: Optional[str],
):
    cpu.imem.load_program(load_hex_file(text_file))

    if data_file is not None:
        cpu.dmem.load_data(load_hex_file(data_file))

    cpu.rst_reg.set(1)
    cpu.rst_reg.update()

    for _ in range(confs.TIMEOUT_ITERATIONS):

        cpu.step()

        rf_dbg = cpu.cpu.rf_inst.read(confs.RF_DBG_NUM)

        if rf_dbg == confs.Test_Result.TEST_RUN.value:
            continue

        if rf_dbg == confs.Test_Result.TEST_PASS.value:
            return

        if rf_dbg == confs.Test_Result.TEST_FAIL.value:
            pytest.fail("Program returned TEST_FAIL")

        raise ValueError(
            f"Invalid RF_DBG value: {rf_dbg:#x}"
        )

    pytest.fail(
        f"Timeout ({confs.TIMEOUT_ITERATIONS} cycles)"
    )


def collect_tests():

    if not LIST_FILE.exists():
        raise FileNotFoundError(LIST_FILE)

    result = []

    with open(LIST_FILE) as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            text = TEST_DIR / line

            data = text.parent / f"{text.stem}_data.hex"

            result.append(
                pytest.param(
                    str(text),
                    str(data) if data.exists() else None,
                    id=text.stem,
                )
            )

    return result


@pytest.fixture
def cpu():
    return cpu_system.CpuSystem()


@pytest.mark.parametrize(
    "text_file,data_file",
    collect_tests(),
)
def test_program(
    cpu,
    text_file,
    data_file,
):
    run_program(
        cpu,
        text_file,
        data_file,
    )