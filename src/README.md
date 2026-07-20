# `src/` – Source Code

This directory is the Python source root of the project. It follows a `src`
layout: all importable packages live directly under `src/` and the package
discovery in `pyproject.toml` is rooted here.

It contains two top-level packages:

- **`risc_v/`** – the RISC-V processor model (shared configuration, reusable
  datapath modules, and the two processor cores).
- **`sim_base/`** – a small, processor-agnostic hardware simulation framework
  (clocks, registers, memories) on which `risc_v` is built.

A standalone entry point, `main.py`, demonstrates loading a program and ticking
the simplest (`risc_v.core`) core by hand.

For the package-level overview see the [root README](../README.md).

## Sub-package Index

| Path | Document | What it contains |
| --- | --- | --- |
| `main.py` | — | Manual simulation driver / usage example. |
| `risc_v/` | [README](risc_v/README.md) | Configuration + modules + cores. |
| `risc_v/base/` | [README](risc_v/base/README.md) | `ICpuSystem` abstract interface. |
| `risc_v/modules/` | [README](risc_v/modules/README.md) | Datapath building blocks. |
| `risc_v/modules/mem/` | [README](risc_v/modules/mem/README.md) | IMEM / DMEM / Register File. |
| `risc_v/pipeline/` | [README](risc_v/pipeline/README.md) | 5-stage pipelined core. |
| `risc_v/pipeline/stages/` | [README](risc_v/pipeline/stages/README.md) | IF/ID/EX/MEM/WB stage logic. |
| `risc_v/single_cycle/` | [README](risc_v/single_cycle/README.md) | Single-cycle core. |
| `sim_base/` | [README](sim_base/README.md) | Simulation framework. |
| `sim_base/core/` | [README](sim_base/core/README.md) | Clock / trigger / combinational interfaces. |
| `sim_base/mem/` | [README](sim_base/mem/README.md) | Register and memory primitives. |

## Architectural Layers (bottom-up)

```text
sim_base/        low-level simulation primitives (Clock, Register, Memories)
   ▲
risc_v/modules/  datapath blocks (ALU, Shifter, BranchUnit, ImmGen, Decode, PC, mem)
   ▲
risc_v/{single_cycle,pipeline}/   processor cores (implement ICpuSystem)
   ▲
tests/           verification, sharing the ICpuSystem contract
```

## Conventions

- All datapath modules expose **static methods** (`Alu.execute`, `ImmGen.generate`,
  `BranchUnit.compare`, `Shifter.shift`, `Instruction_Decoder.decode`, …).
- Stateful, sequential elements (`Register`, `BlockMem`, `RegFile`, pipeline
  buffers) separate a combinational `set()`/`read()` API from an `update()`
  method that commits the next value on a clock tick.
- Instruction values are 32-bit (`conf.XLEN = 32`); registers and memory cells
  are masked to `XLEN` bits.
