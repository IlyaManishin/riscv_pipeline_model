from typing import Optional
import pytest

from risc_v.single_cycle import cpu_system as sc_cpu_system
from tracers.data_tracers import RegisterTracer
from tracers.vcd_tracer import CpuVcdTracer
from tracers.perf_tracers import SingleCyclePerfTracer
from runner import run_program
from benches import *
from tests_config import SC_TRACE_DIR

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


@pytest.fixture
def sc_cpu() -> sc_cpu_system.CpuSystem:
    return sc_cpu_system.CpuSystem()


# ============================================================
# TEST CASES
# ============================================================

@pytest.mark.usefixtures("group_lifecycle")
class TestSingleCycleAsm:
    GROUP_NAME = "asm"

    @pytest.mark.parametrize("test_name, imem_path, dmem_path", ASM_TESTS, ids=ASM_IDS)
    def test_sc_asm(self, sc_cpu: sc_cpu_system.CpuSystem, test_name: str, imem_path: str, dmem_path: Optional[str]) -> None:
        trace_dir = SC_TRACE_DIR / "asm"
        perf_tracer.set_cpu(sc_cpu)
        tracers = [
            RegisterTracer(sc_cpu, trace_dir),
            CpuVcdTracer(sc_cpu, trace_dir),
            perf_tracer
        ]
        run_program(sc_cpu, tracers, test_name, imem_path, dmem_path)


@pytest.mark.usefixtures("group_lifecycle")
class TestSingleCycleC:
    GROUP_NAME = "c"

    @pytest.mark.parametrize("test_name, imem_path, dmem_path", C_TESTS, ids=C_IDS)
    def test_sc_c(self, sc_cpu: sc_cpu_system.CpuSystem, test_name: str, imem_path: str, dmem_path: Optional[str]) -> None:
        trace_dir = SC_TRACE_DIR / "C"
        perf_tracer.set_cpu(sc_cpu)
        tracers = [
            RegisterTracer(sc_cpu, trace_dir),
            CpuVcdTracer(sc_cpu, trace_dir),
            perf_tracer
        ]
        run_program(sc_cpu, tracers, test_name, imem_path, dmem_path)
