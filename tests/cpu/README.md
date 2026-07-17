# `tests/cpu/` – Architectural CPU Verification

This directory contains the architectural-level verification subsystem for the
RISC-V cores. It drives the full processor implementations through the abstract
`ICpuSystem` interface and records cycle-accurate traces. The pipeline
(`test_PL.py`) and single-cycle (`test_SC.py`) cores are validated against the
*same* assembly and C benchmark suites.

See the parent [`../README.md`](../README.md) for the overall framework picture
and the runner/tracer decoupling pattern.

## Files

| File | Description |
| --- | --- |
| `cpu_config.py` | Configuration: `XLEN=32`, `REG_COUNT=32`, `TIMEOUT_ITERATIONS=10000`, signature register `RF_DBG_NUM=31`, trace flags (`TRACE_ENABLE`, `TRACE_DIRNAME="trace"`, `VCD_TRACE_ENABLE`, `VCD_CLOCK_PERIOD_NS`), and `CpuTestResult` enum (`TEST_RUN`/`TEST_PASS`/`TEST_FAIL`). |
| `runner.py` | Black-box execution engine. `load_bin_file`, `load_program` (IMEM/DMEM), `execute_program` (clock loop + signature check), `run_program` (orchestrates tracers incl. VCD), and `collect_tests` (parses the build manifest). Typed against `ICpuSystem`. |
| `tracers.py` | Abstract tracers: `BaseTracer` (lifecycle hooks + `trace_cycle`) and `CsvTracer` (opens/writes a per-test `.csv` under `TRACE_DIRNAME/<name>/`). |
| `data_tracers.py` | Concrete tracers. `RegisterTracer` dumps `cycle, pc, x0..x31`. `PipelineTracer` dumps PC, stall/jump signals, per-stage disassembly, `dmem_sel`, and all registers; introspects the pipeline stages directly. |
| `vcd_tracer.py` | `CpuVcdTracer`: emits a `.vcd` waveform per test via `pyvcd`. Auto-detects pipeline vs single-cycle CPU and defines the matching signal scopes (`cpu`, `registers`, `pipeline/{if,id,ex,mem,wb}` or `single_cycle`). |
| `tests_config.py` | Imports the build manifests through `benchmarks.build_paths` and builds `ASM_TESTS` / `C_TESTS` (plus ids) at import time. |
| `test_PL.py` | Pytest entry-point for the pipelined core (`risc_v.pipeline.cpu_system.CpuSystem`); parametrized over ASM and C tests with `PipelineTracer`. |
| `test_SC.py` | Pytest entry-point for the single-cycle core (`risc_v.single_cycle.cpu_system.CpuSystem`); parametrized over ASM and C tests with `RegisterTracer`. |
| `test_vcd_runner.py` | Integration tests ensuring CSV+VCD are written for the pipeline core and that VCD can be disabled (no `.vcd` emitted). |
| `trace/` | Generated artifacts, split into `pl/` and `sc/` sub-trees (`asm_reg_trace/`, `c_reg_trace/`), each containing `<test>.csv` and `<test>.vcd`. |

## How a Test Runs

1. `tests_config.py` collects `(test_name, imem_path, dmem_path)` tuples from
   the build manifest.
2. The pytest parametrization calls `run_program(cpu, tracers, ...)`.
3. `runner.load_program` streams the compiled binaries into `cpu.imem` /
   `cpu.dmem`.
4. `runner.execute_program` steps the CPU in a loop, calling
   `tracer.trace_cycle(cycle)` each cycle and checking `x31`
   (`RF_DBG_NUM`) for the test signature.
5. Tracers write `trace/<pl|sc>/<name>/<test>.csv`; if `VCD_TRACE_ENABLE`, a
   matching `.vcd` is also written by `CpuVcdTracer`.

## Signature Protocol

Compiled benchmarks write their result to `x31`:

* `0` (`TEST_RUN`) – keep simulating.
* `1` (`TEST_PASS`) – success, stop.
* `2` (`TEST_FAIL`) – fail the pytest case.
* Any other value – invalid signature error.

If the loop reaches `TIMEOUT_ITERATIONS` (10000) without a PASS/FAIL, the test
fails with a timeout (guards against infinite hazard stalls).

## CSV / VCD Output

* CSV traces are always generated when `TRACE_ENABLE` (default `True`); the
  directory is `trace/`.
* VCD traces are generated when `VCD_TRACE_ENABLE` is truthy (default `True`),
  controlled by the `VCD_TRACE_ENABLE` environment variable.
* `tests/utils/disasm.py` supplies human-readable instruction labels inside the
  pipeline CSV trace.
