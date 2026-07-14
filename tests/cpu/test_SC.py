from pathlib import Path
from typing import Optional
import pytest

from risc_v.single_cycle import cpu_system as sc_cpu_system
from tracers import RegisterTracer
from runner import run_program, collect_tests
from benchmarks.build_paths import BUILD_DIR, ASM_DIRNAME, C_DIRNAME

# ============================================================
# TEST SUITE PREPARATION
# ============================================================

# Parse ASM tests
asm_tests = collect_tests(BUILD_DIR / ASM_DIRNAME)
asm_ids = [t[0] for t in asm_tests]

# Parse C tests
c_tests = collect_tests(BUILD_DIR / C_DIRNAME)
c_ids = [t[0] for t in c_tests]


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
    asm_tests,
    ids=asm_ids,
)
def test_sc_asm(
    sc_cpu: sc_cpu_system.CpuSystem,
    test_name: str,
    imem_path: str,
    dmem_path: Optional[str],
) -> None:
    tracers = [
        RegisterTracer(sc_cpu, "asm_reg_trace")
    ]
    run_program(sc_cpu, tracers, test_name, imem_path, dmem_path)


@pytest.mark.parametrize(
    "test_name, imem_path, dmem_path",
    c_tests,
    ids=c_ids,
)
def test_sc_c(
    sc_cpu: sc_cpu_system.CpuSystem,
    test_name: str,
    imem_path: str,
    dmem_path: Optional[str],
) -> None:
    tracers = [
        RegisterTracer(sc_cpu, "c_reg_trace")
    ]
    run_program(sc_cpu, tracers, test_name, imem_path, dmem_path)
