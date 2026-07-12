from pathlib import Path
from typing import Optional
import pytest

from risc_v.single_cycle import cpu_system as sc_cpu_system
from tracers import SingleCycleTracer
from runner import run_program, collect_tests
from bench_builder.build_paths import BUILD_DIR, ASM_DIRNAME


@pytest.fixture
def sc_cpu() -> sc_cpu_system.CpuSystem:
    return sc_cpu_system.CpuSystem()


@pytest.mark.parametrize(
    "text_file, data_file",
    collect_tests(BUILD_DIR / ASM_DIRNAME),
)
def test_sc_asm(
    sc_cpu: sc_cpu_system.CpuSystem,
    text_file: str,
    data_file: Optional[str],
) -> None:
    tracer = SingleCycleTracer(sc_cpu, Path(text_file).stem)
    run_program(sc_cpu, tracer, text_file, data_file)
