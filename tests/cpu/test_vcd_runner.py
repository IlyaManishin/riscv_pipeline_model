from pathlib import Path

import runner
from data_tracers import PipelineTracer, RegisterTracer
from risc_v.pipeline.cpu_system import CpuSystem as PipelineCpuSystem
from risc_v.single_cycle.cpu_system import CpuSystem as SingleCycleCpuSystem


PASS_PROGRAM = (0x00100F93).to_bytes(4, byteorder="little")


def test_runner_writes_vcd_next_to_pipeline_csv(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner, "VCD_TRACE_ENABLE", True)

    program = tmp_path / "pass.bin"
    program.write_bytes(PASS_PROGRAM)
    cpu = PipelineCpuSystem()
    tracer = PipelineTracer(cpu, "pl/integration_trace")

    runner.run_program(cpu, [tracer], "pass", str(program), None)

    trace_dir = tmp_path / "trace" / "pl" / "integration_trace"
    assert (trace_dir / "pass.csv").is_file()
    vcd_path = trace_dir / "pass.vcd"
    assert vcd_path.is_file()

    vcd = vcd_path.read_text(encoding="utf-8")
    assert "$timescale 1 ns $end" in vcd
    assert "$scope module pipeline $end" in vcd
    assert "$scope module wb $end" in vcd
    assert "$enddefinitions $end" in vcd


def test_runner_can_disable_vcd(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner, "VCD_TRACE_ENABLE", False)

    program = tmp_path / "pass.bin"
    program.write_bytes(PASS_PROGRAM)
    cpu = SingleCycleCpuSystem()
    tracer = RegisterTracer(cpu, "sc/integration_trace")

    runner.run_program(cpu, [tracer], "pass", str(program), None)

    trace_dir = tmp_path / "trace" / "sc" / "integration_trace"
    assert (trace_dir / "pass.csv").is_file()
    assert not (trace_dir / "pass.vcd").exists()
