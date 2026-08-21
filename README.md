# 🚀 RISC-V Pipeline Model

A cycle-accurate, RTL-style simulator of a 32-bit RISC-V processor (RV32I base ISA) written in pure Python. 

Designed to intentionally mirror true hardware semantics, the simulator evaluates combinational logic into "next" states that are committed only on a clock tick. This approach makes the model ideal for teaching, waveform inspection (VCD), and cycle-accurate architectural verification.

### 🧠 Core Architectures
The project features two microarchitectures that share a common instruction set and module library (ALU, Register File, memory interfaces, etc.):

*   **Single-Cycle Core:** Executes one instruction per clock cycle.
*   **5-Stage Pipelined Core:** Features a classic IF / ID / EX / MEM / WB pipeline equipped with a dedicated hazard detection unit.

Both cores operate on top of a custom hardware-simulation framework (`sim_base`) providing clocked registers, sync/async memories, and a foundational clock primitive.

---

## ✨ Key Features

*   **Full RV32I Support:** Executes all standard base instructions, including jumps, branches, memory loads/stores, and ALU operations.
*   **Unified Testing & High Coverage:** Both cores share the same `ICpuSystem` interface. A solid suite of 57 automated tests ensures both designs work correctly.
*   **Automated Benchmark Execution:** Includes a built-in system that automatically compiles and runs complex assembly and C programs to test the CPU.
*   **Advanced Hazard Handling:** The pipelined core automatically resolves control hazards (jumps/branches) and data hazards out of the box.
*   **Hardware-Accurate Memory:** Models real synchronous block memory. It updates safely on clock ticks and supports byte-level masking for precise memory writes.
*   **Detailed CSV Tracing:** Generates cycle-by-cycle CSV logs to monitor the CPU state. It tracks the program counter, pipeline stages, hazard unit, and all registers for easy debugging.

## Project Layout

```text
riscv_pipeline_model/
├── src/                      # All source code (see src/README.md)
│   ├── main.py              # Example entry point / manual simulation driver
│   ├── risc_v/              # RISC-V model (config, modules, cores)
│   │   ├── base/            # Abstract ICpuSystem interface
│   │   ├── modules/         # Reusable datapath building blocks
│   │   │   └── mem/         # IMEM / DMEM / Register File
│   │   ├── pipeline/        # 5-stage pipelined core
│   │   │   └── stages/      # IF / ID / EX / MEM / WB stages
│   │   └── single_cycle/    # Single-cycle core
│   └── sim_base/            # Hardware simulation framework
│       ├── core/            # Abstract clock / trigger / combinational interfaces
│       └── mem/             # Register, BlockMem, AsyncReadMem, MultiWriteMem
├── tests/                   # Verification suite (see tests/README.md)
│   ├── cpu/                 # Architectural CPU verification + tracers
│   ├── modules/             # Unit tests for IMEM / DMEM / RegFile
│   ├── sim_base/            # Tests for the simulation framework
│   └── utils/               # disasm helper
├── benchmarks/              # Assembly + C benchmark sources and build scripts
├── trace/                   # Generated CSV / VCD waveforms (output)
├── pyproject.toml           # Package metadata, pytest config
└── reqs.txt                 # Pinned dependencies

```

---

## Installation

Requires Python 3.11+.

```bash
python -m pip install -r reqs.txt
```

Key runtime dependencies:

* `pyvcd>=0.4.1,<0.5` – writes VCD waveform files.
* `pytest==9.0.2` – test runner.
* `cocotb==2.0.1`, `find_libpython`, `tqdm`, etc. – used by the
`benchmarks/` build / comparison tooling.

The package uses an editable-style layout (`[tool.setuptools.packages.find]`
with `where = ["src"]`), so the `src` layout is importable directly when
`src` is on `PYTHONPATH` (configured in `pyproject.toml` `[tool.pytest.ini_options]`).

---

## Quick Start
Drive the full cores programmatically:

```python
from risc_v.pipeline import cpu_system as pl
from risc_v.single_cycle import cpu_system as sc

pl_cpu = pl.CpuSystem()

pl_cpu.imem.load_program(instructions)   # list[int], 32-bit each
pl_cpu.dmem.load_data(data)
pl_cpu.step()                            # advances one clock edge
```

---

## Running the Tests

To run the test suite, execute:

```bash
pytest

```

For advanced test options, custom flags, and details on verification, see [`tests/README.md`](https://www.google.com/search?q=tests/README.md).

---

## Documentation Map

| Document | Scope |
| --- | --- |
| `src/README.md` | Source tree overview |
| `src/risc_v/README.md` | RISC-V model layers |
| `src/risc_v/modules/README.md` | Datapath building blocks |
| `src/risc_v/pipeline/README.md` | Pipelined core |
| `src/risc_v/pipeline/stages/README.md` | Pipeline stages |
| `src/risc_v/single_cycle/README.md` | Single-cycle core |
| `src/sim_base/README.md` | Simulation framework |
| `tests/README.md` | Verification suite |
| `tests/cpu/README.md` | Architectural CPU tests & tracers |