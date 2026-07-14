from pathlib import Path
from typing import Optional
import pytest

from risc_v.pipeline import cpu_system as sc_cpu_system
from tracers import PipelineTracer
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
    "test_name, text_file, data_file",
    asm_tests,
    ids=asm_ids,
)
def test_sc_asm(
    sc_cpu: sc_cpu_system.CpuSystem,
    test_name: str,
    text_file: str,
    data_file: Optional[str],
) -> None:
    tracer = PipelineTracer(sc_cpu, test_name)
    run_program(sc_cpu, tracer, text_file, data_file)


@pytest.mark.parametrize(
    "test_name, text_file, data_file",
    c_tests,
    ids=c_ids,
)
def test_sc_c(
    sc_cpu: sc_cpu_system.CpuSystem,
    test_name: str,
    text_file: str,
    data_file: Optional[str],
) -> None:
    tracer = PipelineTracer(sc_cpu, test_name)
    run_program(sc_cpu, tracer, text_file, data_file)