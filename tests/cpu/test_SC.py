import pytest

from risc_v.base.icpu_system import ICpuSystem
from models.single_cycle import cpu_system as sc_cpu_system
from tracers.data_tracers import RegisterTracer
from tracers.vcd_tracer import CpuVcdTracer
from tracers.perf_tracers import SingleCyclePerfTracer
from runner import run_program
from benches import CpuTestConfig, ASM_TESTS, ASM_IDS, C_TESTS, C_IDS
from tests_config import SC_TRACE_DIR, size_to_addr_width

# ============================================================
# CPU INITIALIZATION HELPERS
# ============================================================


def create_sc_cpu(test_config: CpuTestConfig) -> ICpuSystem:
    imem_addr_width = size_to_addr_width(test_config.imem_size)
    dmem_addr_width = size_to_addr_width(test_config.dmem_size)
    return sc_cpu_system.CpuSystem(
        imem_addr_width=imem_addr_width,
        dmem_addr_width=dmem_addr_width
    )


# ============================================================
# STATIC_TRACERS + FIXTURES
# ============================================================
perf_tracer = SingleCyclePerfTracer(SC_TRACE_DIR)


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
class TestSingleCycleAsm:
    GROUP_NAME = "asm"

    @pytest.mark.parametrize("test_config", ASM_TESTS, ids=ASM_IDS)
    def test_sc_asm(self, test_config: CpuTestConfig) -> None:
        sc_cpu = create_sc_cpu(test_config)

        trace_dir = SC_TRACE_DIR / "asm"
        perf_tracer.set_cpu(sc_cpu)
        tracers = [
            RegisterTracer(sc_cpu, trace_dir),
            CpuVcdTracer(sc_cpu, trace_dir),
            perf_tracer
        ]
        run_program(sc_cpu, tracers, test_config)


@pytest.mark.usefixtures("group_lifecycle")
class TestSingleCycleC:
    GROUP_NAME = "c"

    @pytest.mark.parametrize("test_config", C_TESTS, ids=C_IDS)
    def test_sc_c(self, test_config: CpuTestConfig) -> None:
        sc_cpu = create_sc_cpu(test_config)

        trace_dir = SC_TRACE_DIR / "C"
        perf_tracer.set_cpu(sc_cpu)
        tracers = [
            RegisterTracer(sc_cpu, trace_dir),
            CpuVcdTracer(sc_cpu, trace_dir),
            perf_tracer
        ]
        run_program(sc_cpu, tracers, test_config)
