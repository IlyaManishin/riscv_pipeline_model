from typing import Optional
import pytest

from risc_v.pipeline import cpu_system as pl_cpu_system
from tracers.data_tracers import PipelineTracer
from tracers.vcd_tracer import CpuVcdTracer
from runner import run_program
from benches import *
from tests_config import PL_TRACE_DIR


@pytest.fixture
def pl_cpu() -> pl_cpu_system.CpuSystem:
    return pl_cpu_system.CpuSystem()


@pytest.mark.parametrize(
    "test_name, imem_path, dmem_path",
    ASM_TESTS,
    ids=ASM_IDS,
)
def test_pipeline_asm(
    pl_cpu: pl_cpu_system.CpuSystem,
    test_name: str,
    imem_path: str,
    dmem_path: Optional[str],
) -> None:
    tracers = [
        PipelineTracer(pl_cpu, PL_TRACE_DIR / "asm"),
        CpuVcdTracer(pl_cpu, PL_TRACE_DIR / "asm")
    ]
    run_program(pl_cpu, tracers, test_name, imem_path, dmem_path)


@pytest.mark.parametrize(
    "test_name, imem_path, dmem_path",
    C_TESTS,
    ids=C_IDS,
)
def test_pipeline_c(
    pl_cpu: pl_cpu_system.CpuSystem,
    test_name: str,
    imem_path: str,
    dmem_path: Optional[str],
) -> None:
    tracers = [
        PipelineTracer(pl_cpu, PL_TRACE_DIR / "C"),
        CpuVcdTracer(pl_cpu, PL_TRACE_DIR / "C"),
    ]
    run_program(pl_cpu, tracers, test_name, imem_path, dmem_path)