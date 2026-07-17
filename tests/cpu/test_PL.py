from typing import Optional
import pytest

from risc_v.pipeline import cpu_system as pl_cpu_system
from tracers.data_tracers import PipelineTracer
from tracers.vcd_tracer import CpuVcdTracer
from runner import run_program
from tests_config import ASM_TESTS, ASM_IDS, C_TESTS, C_IDS


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
        PipelineTracer(pl_cpu, "pl/asm_reg_trace"),
        CpuVcdTracer(pl_cpu, "pl/asm_vcd_trace")
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
        PipelineTracer(pl_cpu, "pl/c_reg_trace"),
        CpuVcdTracer(pl_cpu, "pl/c_vcd_trace"),
    ]
    run_program(pl_cpu, tracers, test_name, imem_path, dmem_path)