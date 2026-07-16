# RISC-V Pipeline Model

A cycle-accurate, RTL-style simulator of a 32-bit RISC-V processor (RV32I base
ISA) written in pure Python. The project models two processor microarchitectures
sharing a common instruction set and module library:

- **Single-cycle core** (`src/risc_v/single_cycle/`) – one instruction per clock.
- **5-stage pipelined core** (`src/risc_v/pipeline/`) – classic IF / ID / EX /
  MEM / WB pipeline with a hazard detection unit.

Both cores are built from the same reusable building blocks (`ALU`, `Register
File`, `immediate generator`, `branch unit`, `shifter`, memory interfaces) and
sit on top of a small hardware-simulation framework (`sim_base`) that provides
clocked `Register`s, synchronous/asynchronous memories, and a `Clock` primitive.

The design intentionally mirrors hardware semantics: combinational logic is
evaluated into "next" values that are committed only on a clock `tick()`. This
makes the model suitable for teaching, waveform inspection (VCD), and
cycle-accurate architectural verification against compiled assembly / C
benchmarks.

---

## Features

- RV32I support: LUI, AUIPC, JAL, JALR, branches (BEQ/BNE/BLT/BGE/BLTU/BGEU),
  loads (LB/LH/LW/LBU/LHU), stores (SB/SH/SW), and the full ALU/shift set
  (ADD/SUB/SLT/SLTU/AND/OR/XOR/SLL/SRL/SRA/LUI).
- Single-cycle and 5-stage pipelined implementations behind one `ICpuSystem`
  interface, so the same test harness drives both.
- Hazard handling (control hazards for jumps/branches, RAW data hazards) in the
  pipelined core via the `Hazard_Detection_Unit`.
- Byte-addressable, sub-word data memory with byte-write-enable masking.
- `x0` hard-wired to zero, register-file reset enforcement.
- Cycle-accurate CSV register traces and VCD waveform dumps for both cores.

---

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

- `pyvcd>=0.4.1,<0.5` – writes VCD waveform files.
- `pytest==9.0.2` – test runner.
- `cocotb==2.0.1`, `find_libpython`, `tqdm`, etc. – used by the
  `benchmarks/` build / comparison tooling.

The package uses an editable-style layout (`[tool.setuptools.packages.find]`
with `where = ["src"]`), so the `src` layout is importable directly when
`src` is on `PYTHONPATH` (configured in `pyproject.toml` `[tool.pytest.ini_options]`).

---

## Quick Start

Run a small program manually from `src/main.py` (loads a `.hex` instruction
file and ticks the core):

```python
from risc_v import core

core = core.Core(2**10, 2**10)
core.upload_instr_from_hex("path/to/program.hex")
for _ in range(20):
    core.tick()
```

> Note: `risc_v/core.py` is a third, minimal "flat" single-file core used by
> `main.py`. The full, microarchitecture-correct cores live under
> `risc_v/single_cycle/` and `risc_v/pipeline/` and are the ones exercised by
> the test suite.

Drive the full cores programmatically:

```python
from risc_v.pipeline import cpu_system as pl
from risc_v.single_cycle import cpu_system as sc

pl_cpu = pl.CpuSystem()
sc_cpu = sc.CpuSystem()

pl_cpu.imem.load_program(instructions)   # list[int], 32-bit each
pl_cpu.dmem.load_data(data)
pl_cpu.step()                            # advances one clock edge
```

---

## Running the Tests

From the project root:

```bash
# Full regression (unit tests + CPU benchmarks)
python -m pytest -v

# Architectural CPU validation only
python -m pytest -v tests/cpu/

# Module-level unit tests only
python -m pytest -v tests/modules/
```

CPU benchmarks are discovered from build manifests produced by the
`benchmarks/` build scripts (`benchmarks/build_paths.py:TEST_LIST_NAME`). The
pipeline and single-cycle cores are parametrized over the same assembly and C
suites, so any benchmark that passes for one core is validated against the
other.

VCD waveform generation is enabled by default and controlled by the
`VCD_TRACE_ENABLE` environment variable; CSV tracing is controlled by
`TRACE_ENABLE` in `tests/cpu/cpu_config.py`. See `tests/README.md` for details.

---

## Documentation Map

| Document | Scope |
| --- | --- |
| `src/README.md` | Source tree overview and index of sub-package READMEs |
| `src/risc_v/README.md` | RISC-V model layers |
| `src/risc_v/base/README.md` | `ICpuSystem` interface |
| `src/risc_v/modules/README.md` | Datapath building blocks |
| `src/risc_v/modules/mem/README.md` | Memory components |
| `src/risc_v/pipeline/README.md` | Pipelined core |
| `src/risc_v/pipeline/stages/README.md` | Pipeline stages |
| `src/risc_v/single_cycle/README.md` | Single-cycle core |
| `src/sim_base/README.md` | Simulation framework |
| `src/sim_base/core/README.md` | Clock/trigger interfaces |
| `src/sim_base/mem/README.md` | Memory primitives |
| `tests/README.md` | Verification suite (updated) |
| `tests/cpu/README.md` | Architectural CPU tests & tracers |
