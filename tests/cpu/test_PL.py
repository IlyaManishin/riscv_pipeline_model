from typing import Optional
import pytest

from risc_v.pipeline import cpu_system as pl_cpu_system
from tracers.data_tracers import PipelineTracer
from tracers.vcd_tracer import CpuVcdTracer
from tracers.perf_tracers import PipelinePerfTracer
from runner import run_program
from benches import *
from tests_config import PL_TRACE_DIR

# ============================================================
# STATIC_TRACERS + FIXTURES
# ============================================================

perf_tracer = PipelinePerfTracer(PL_TRACE_DIR)


@pytest.fixture(scope="class")
def group_lifecycle(request):
    group_name = getattr(request.cls, "GROUP_NAME", "unknown")
    perf_tracer.on_group_start(group_name)
    yield
    perf_tracer.on_group_end()


@pytest.fixture
def pl_cpu() -> pl_cpu_system.CpuSystem:
    return pl_cpu_system.CpuSystem()

# ============================================================
# TEST CASES
# ============================================================


@pytest.mark.usefixtures("group_lifecycle")
class TestPipelineAsm:
    GROUP_NAME = "asm"

    @pytest.mark.parametrize("test_name, imem_path, dmem_path", ASM_TESTS, ids=ASM_IDS)
    def test_pipeline_asm(self, pl_cpu: pl_cpu_system.CpuSystem, test_name: str, imem_path: str, dmem_path: Optional[str]) -> None:
        trace_dir = PL_TRACE_DIR / "asm"
        perf_tracer.set_cpu(pl_cpu)
        tracers = [
            PipelineTracer(pl_cpu, trace_dir),
            CpuVcdTracer(pl_cpu, trace_dir),
            perf_tracer
        ]
        run_program(pl_cpu, tracers, test_name, imem_path, dmem_path)


@pytest.mark.usefixtures("group_lifecycle")
class TestPipelineC:
    GROUP_NAME = "c"

    @pytest.mark.parametrize("test_name, imem_path, dmem_path", C_TESTS, ids=C_IDS)
    def test_pipeline_c(self, pl_cpu: pl_cpu_system.CpuSystem, test_name: str, imem_path: str, dmem_path: Optional[str]) -> None:
        trace_dir = PL_TRACE_DIR / "C"
        perf_tracer.set_cpu(pl_cpu)
        tracers = [
            PipelineTracer(pl_cpu, trace_dir),
            CpuVcdTracer(pl_cpu, trace_dir),
            perf_tracer
        ]
        run_program(pl_cpu, tracers, test_name, imem_path, dmem_path)
