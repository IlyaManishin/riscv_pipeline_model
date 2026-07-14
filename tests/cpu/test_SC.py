from typing import Optional
import pytest

from risc_v.single_cycle import cpu_system as sc_cpu_system
from data_tracers import RegisterTracer
from runner import run_program
from tests_config import ASM_TESTS, ASM_IDS, C_TESTS, C_IDS


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def sc_cpu() -> sc_cpu_system.CpuSystem:
    return sc_cpu_system.CpuSystem()


# ============================================================
# TEST CASES
# ============================================================

@pytest.mark.parametrize(
    "test_name, imem_path, dmem_path",
    ASM_TESTS,
    ids=ASM_IDS,
)
def test_sc_asm(
    sc_cpu: sc_cpu_system.CpuSystem,
    test_name: str,
    imem_path: str,
    dmem_path: Optional[str],
) -> None:
    tracers = [
        RegisterTracer(sc_cpu, "sc/asm_reg_trace")
    ]
    run_program(sc_cpu, tracers, test_name, imem_path, dmem_path)


@pytest.mark.parametrize(
    "test_name, imem_path, dmem_path",
    C_TESTS,
    ids=C_IDS,
)
def test_sc_c(
    sc_cpu: sc_cpu_system.CpuSystem,
    test_name: str,
    imem_path: str,
    dmem_path: Optional[str],
) -> None:
    tracers = [
        RegisterTracer(sc_cpu, "sc/c_reg_trace")
    ]
    run_program(sc_cpu, tracers, test_name, imem_path, dmem_path)
