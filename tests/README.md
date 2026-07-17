# 🧪 Processor Verification & Test Automation Framework (`tests`)

This framework provides a layered verification suite for the RISC-V processor
model, ranging from low-level unit testing of digital primitives to full
architectural validation using compiled assembly and high-level C benchmarks.

---

## 📂 Directory Structure

```text
tests/
├── cpu/                   # Architectural-level CPU verification
│   ├── cpu_config.py      # Execution bounds, constants, signature mapping, trace flags
│   ├── runner.py          # Decoupled simulation driver and test discovery
│   ├── tracers.py         # Abstract tracer base classes (BaseTracer, CsvTracer)
│   ├── data_tracers.py    # Concrete state-introspection tracers (Register, Pipeline)
│   ├── vcd_tracer.py      # VCD waveform tracer (pyvcd)
│   ├── tests_config.py    # Collects ASM and C test lists at import time
│   ├── test_PL.py         # Pytest entry-point for pipelined core regression
│   ├── test_SC.py         # Pytest entry-point for single-cycle core regression
│   ├── tracers.py         # Concrete state-introspection analytics engines
│   └── test_SC.py         # Pytest entry-point for single-cycle core regression
│
├── modules/               # Isolated component-level unit tests
│   ├── test_imem.py       # Instruction memory boundary validations
│   ├── test_dmem.py       # Data memory byte-masking and write-conflict tests
│   └── test_register_file.py # RegFile multi-port access verification
│
├── sim_base/              # Simulation engine primitive validation
│   └── test_bmem.py       # BlockMem single-address contention test cases
│
└── utils/                 # Shared test utilities
    └── disasm.py          # 32-bit RISC-V instruction disassembler (for trace labels)
```

For a deep dive into the CPU subsystem, see [`cpu/README.md`](cpu/README.md).

---

## ⚙️ Architectural CPU Verification (`tests/cpu`)

The architectural test subsystem is designed around a strict decoupling pattern.
It separates test orchestration (black-box simulation execution) from
verification data gathering (white-box state extraction).

```
   [ Test Artifacts ] (.bin) ──> runner.py (Black-Box Loader)
                                      │
                         Uses abstract ICpuSystem interface
                                      │
                                      ▼
    [ tracers.py / data_tracers.py ] ◄──(Inspects)── CpuSystem (Concrete Model Execution)
    (White-Box Dump)
```

### 1. Interface-Driven Isolation (`runner.py`)

The execution orchestrator (`runner.py`) handles binary asset distribution and
execution scheduling. To ensure complete target independence, **the runner
operates as a black box and has zero knowledge of the processor's internal
microarchitecture.** It interacts strictly with the abstract `ICpuSystem`
layout interface:

* **Memory Load Operations**: `load_program()` streams compiled binaries into
  `cpu.imem.load_program()` and `cpu.dmem.load_data()` for instruction and data
  channels before execution.
* **Deterministic Steps**: Drives processing purely via the single-edge
  interface method `cpu.step()`.
* **Architecture-Agnostic Execution**: The exact same runner loop drives the
  single-cycle and pipelined cores, because both implement `ICpuSystem`.

### 2. Microarchitectural Introspection (`tracers.py` / `data_tracers.py`)

While the runner is decoupled, the tracking infrastructure behaves as a
**white-box diagnostics tool**.

* The tracer holds a reference to the concrete processor top-level instance
  (e.g., `CpuSystem`), or to specific stages for the pipeline tracer.
* It extracts internal state each cycle: the PC (`cpu.get_cur_pc()`), every
  general-purpose register (`cpu.reg_file.read(i)`), and – for the pipeline
  tracer – per-stage instruction disassembly and control signals
  (`jfexe`, `jfid`, `alures`, `imm_pc`, `dmem_sel`, …).
* Data is captured into a cycle-accurate `.csv` manifest, with optional
  disassembly labels produced by `tests/utils/disasm.py`.

### 3. Benchmark Constraints & Signature Tracking

Test completion is governed by the general-purpose register **`x31`**
(`RF_DBG_NUM`) inside `cpu_config.py`:

* **`CpuTestResult.TEST_RUN` (`0`)**: Simulation frame remains active.
* **`CpuTestResult.TEST_PASS` (`1`)**: Program terminated safely; functional
  criteria verified.
* **`CpuTestResult.TEST_FAIL` (`2`)**: Functional check failed during execution.

If a test fails to update `x31` within a hard boundary (`TIMEOUT_ITERATIONS =
10000`), the runner terminates the loop with an explicit timeout failure to
catch infinite hazard loops.

---

## 📦 Test Data Discovery & Pipeline Integration

Pytest modules automatically map validation targets using centralized manifests
produced by the `benchmarks/` build scripts:

1. Tests are parameterized dynamically by scanning the build manifests:
   * **Assembly Suite**: `benchmarks/build/asm/` manifest
     (`benchmarks/build_paths.TEST_LIST_NAME`).
   * **C Benchmarks**: `benchmarks/build/C/` manifest.
2. `collect_tests()` (`runner.py`) parses comma-separated records
   (`<test_name>,<imem_path>,<dmem_path>`).
3. Each entry spawns an isolated execution environment, loading the instruction
   stream and (optional) data segment into the target CPU before stepping.
4. `tests_config.py` builds `ASM_TESTS` / `C_TESTS` (and their ids) at import
   time, which `test_PL.py` and `test_SC.py` consume via
   `@pytest.mark.parametrize`.

---

## 🛠️ Unit & Module-Level Verification

### 1. Hardware Primitives (`tests/sim_base`)

Validates fundamental execution requirements enforced by the custom Python
hardware engine framework. For instance, `test_bmem.py` validates that
`BlockMem` flags multiple address modifications / multiple reads within a
single clock cycle as an error.

### 2. Processor Modules (`tests/modules`)

Validates the decoupled logical sub-blocks before integration into the
top-level structure:

* **`test_register_file.py`**: Ensures concurrent dual-read access works and
  `x0` stays zero.
* **`test_dmem.py` / `test_imem.py`**: Verifies address misalignment handling,
  byte write-masking, single-write-per-cycle constraints, and bounds checks.

---

## 🚀 Running Tests

To run the full regression test suite (unit tests and CPU benchmarks), execute
`pytest` from the project workspace:

```bash
# Run all verification modules
python -m pytest -v

# Run architectural CPU validation tests only
python -m pytest -v tests/cpu/

# Run modular unit tests only
python3 -m pytest -v tests/modules/

```