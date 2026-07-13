# 🧪 Processor Verification & Test Automation Framework(`tests`)

This framework provides a layered verification suite for the RISC-V processor model, ranging from low-level unit testing of digital primitives to full architectural validation using compiled assembly and high-level C benchmarks.

---

## 📂 Directory Structure

```text
tests/
├── cpu/                   # Architectural-level CPU verification
│   ├── cpu_config.py      # Execution bounds, constants, and signature mapping
│   ├── runner.py          # Decoupled simulation driver and test discovery
│   ├── tracers.py         # Concrete state-introspection analytics engines
│   └── test_SC.py         # Pytest entry-point for single-cycle core regression
│
├── modules/               # Isolated component-level unit tests
│   ├── test_imem.py       # Instruction memory boundary validations
│   ├── test_dmem.py       # Data memory byte-masking and write-conflict tests
│   └── test_register_file.py # RegFile multi-port access verification
│
└── sim_base/              # Simulation engine primitive validation
    └── test_bmem.py       # BlockMem single-address contention test cases

```

---

## ⚙️ Architectural CPU Verification (`tests/cpu`)

The architectural test subsystem is designed around a strict decoupling pattern. It separates test orchestration (black-box simulation execution) from verification data gathering (white-box state extraction).

```
   [ Test Artifacts ] (.bin) ──> runner.py (Black-Box Loader)
                                     │
                        Uses abstract ICpuSystem interface
                                     │
                                     ▼
   [ tracers.py ] ◄──(Inspects)── CpuSystem (Concrete Model Execution)
   (White-Box Dump)

```

### 1. Interface-Driven Isolation (`runner.py`)

The execution orchestrator (`runner.py`) handles binary asset distribution and execution scheduling. To ensure complete target independence, **the runner operates as a black box and has zero knowledge of the processor's internal microarchitecture.** It interacts strictly with the abstract `ICpuSystem` layout interface:

* **Memory Load Operations**: Directly exposes `cpu.imem.load_program()` and `cpu.dmem.load_data()` to stream compiled binary chunks into independent instruction and data channels prior to assertion.
* **Deterministic Steps**: Controls processing advances purely via the single-cycle interface method `cpu.step()`.
* **Architecture-Agnostic Execution**: The exact same runner orchestration loop can drive a single-cycle, multi-cycle, or pipelined processor, as long as the concrete top-level class implements `ICpuSystem`.

### 2. Microarchitectural Introspection (`tracers.py`)

While the runner is completely decoupled, the tracking infrastructure (`tracers.py`) behaves as a **white-box diagnostics tool**.

* The tracer holds a reference to the concrete, explicit processor top-level instance (e.g., `CpuSystem`).
* It possesses full introspection access to extract internal states, including the Program Counter (`pc_inst.read()`), source/destination register configurations (`rs1`, `rs2`, `rd`), and the absolute content tracking array of all 32 general-purpose registers (`rf_inst.read(i)`).
* On every clock cycle, this data is captured and exported into a cycle-accurate `.csv` manifest for execution waveform post-processing.

### 3. Benchmark Constraints & Signature Tracking

Test completion criteria and status evaluation are governed by execution structures defined during benchmark cross-compilation.
Execution control loops observe the general-purpose register **`x31`** (`RF_DBG_NUM`), tracking changes inside the Register File interface:

* **`CpuTestResult.TEST_RUN` (`0`)**: Simulation frame remains active.
* **`CpuTestResult.TEST_PASS` (`1`)**: Program terminated safely; functional criteria verified.
* **`CpuTestResult.TEST_FAIL` (`2`)**: Functional check failed during execution.

If a test fails to update `x31` within a hard boundary ceiling (`TIMEOUT_ITERATIONS = 50000`), the runner terminates the loop with an explicit timeout crash to catch infinite hazard loops.

---

## 📦 Test Data Discovery & Pipeline Integration

Pytest modules automatically query and map validation targets using centralized serialization points inside the build matrix.

1. Tests are parameterized dynamically by scanning the automated build logs:
* **Assembly Suite**: `benchmarks/build/asm/benches.lst`
* **C Benchmarks**: `benchmarks/build/C/benches.lst`


2. The `collect_tests()` parser extracts individual comma-separated structures (`<test_name>,<imem_path>,<dmem_path>`).
3. Each entry spawns an isolated execution environment instance, loading the extracted instruction streams and localized data boundaries into the target context slots sequentially.

---

## 🛠️ Unit & Module-Level Verification

To isolate bugs before scaling to complete processor validation loop cycles, component blocks are tested independently using isolated unit contexts.

### 1. Hardware Primitives (`tests/sim_base`)

Validates fundamental execution requirements enforced by the custom Python hardware engine framework. For instance, `test_bmem.py` validates that `BlockMem` successfully flags multiple address modifications within a single clock cycle boundary as an analytical error.

### 2. Processor Modules (`tests/modules`)

Validates the decoupled logical sub-blocks of the design before integration into the top-level structure:

* **`test_register_file.py`**: Ensures concurrent dual-read access parameters function correctly and values are latched properly.
* **`test_dmem.py` / `test_imem.py**`: Verifies address misalignment handling, byte write-masking, and standard range check constraints.

---

## 🚀 Running Tests

To run the full regression test suite (both unit tests and CPU benchmarks), execute `pytest` from the project workspace:

```bash
# Run all verification modules
python3 -m pytest -v

# Run architectural CPU validation tests only
python3 -m pytest -v tests/cpu/

# Run modular unit tests only
python3 -m pytest -v tests/modules/

```