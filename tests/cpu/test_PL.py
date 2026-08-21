import pytest

from risc_v.base.icpu_system import ICpuSystem
from models.pipeline import cpu_system as pl_cpu_system
from tracers.data_tracers import PipelineTracer
from tracers.vcd_tracer import CpuVcdTracer
from tracers.perf_tracers import PipelinePerfTracer
from runner import run_program
from benches import CpuTestConfig, ASM_TESTS, ASM_IDS, C_TESTS, C_IDS
from tests_config import PL_TRACE_DIR, size_to_addr_width

# ============================================================
# CPU INITIALIZATION HELPERS
# ============================================================


def create_pl_cpu(test_config: CpuTestConfig) -> ICpuSystem:
    imem_addr_width = size_to_addr_width(test_config.imem_size)
    dmem_addr_width = size_to_addr_width(test_config.dmem_size)
    return pl_cpu_system.CpuSystem(
        imem_addr_width=imem_addr_width,
        dmem_addr_width=dmem_addr_width
    )


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

# ============================================================
# TEST CASES
# ============================================================


@pytest.mark.usefixtures("group_lifecycle")
class TestPipelineAsm:
    GROUP_NAME = "asm"

    @pytest.mark.parametrize("test_config", ASM_TESTS, ids=ASM_IDS)
    def test_pipeline_asm(self, test_config: CpuTestConfig) -> None:
        pl_cpu = create_pl_cpu(test_config)

        trace_dir = PL_TRACE_DIR / "asm"
        perf_tracer.set_cpu(pl_cpu)
        tracers = [
            PipelineTracer(pl_cpu, trace_dir),
            CpuVcdTracer(pl_cpu, trace_dir),
            perf_tracer
        ]
        run_program(pl_cpu, tracers, test_config)


@pytest.mark.usefixtures("group_lifecycle")
class TestPipelineC:
    GROUP_NAME = "c"

    @pytest.mark.parametrize("test_config", C_TESTS, ids=C_IDS)
    def test_pipeline_c(self, test_config: CpuTestConfig) -> None:
        pl_cpu = create_pl_cpu(test_config)

        trace_dir = PL_TRACE_DIR / "C"
        perf_tracer.set_cpu(pl_cpu)
        tracers = [
            PipelineTracer(pl_cpu, trace_dir),
            CpuVcdTracer(pl_cpu, trace_dir),
            perf_tracer
        ]
        run_program(pl_cpu, tracers, test_config)
