# `risc_v/modules/mem/` – Memory Components

Memory-backed building blocks for the processor. All three subclass primitives
from [`sim_base/mem/`](../../sim_base/mem/README.md) and therefore inherit the
synchronous-write / `update()`-on-clock-tick semantics.

## `imem.py` – `InstrMem`

Subclass of `sim_base.mem.BlockMem` (cell-addressed, synchronous, byte-masked).

- Read-only during simulation: `write()` raises `PermissionError`.
- `load_program(program_code: list[int])` – bulk-loads 32-bit instruction words
  into contiguous cells (bounds-checked, masked to `XLEN`).

## `dmem.py` – `DataMem`

Subclass of `sim_base.mem.BlockMem`.

- `load_data(data: list[int])` – bulk-loads an initial data segment
  (bounds-checked, masked to `XLEN`).
- Supports runtime byte/halfword/word reads and writes via `byte_we` masking,
  driven by the `dmem_*_port` helpers in the parent `modules/` directory.

## `reg_file.py` – `RegFile`

Subclass of `sim_base.mem.AsyncReadMem` (asynchronous reads, synchronous write).

- `REG_COUNT = 32`, `REG_WIDTH = XLEN`.
- `read(address)` – always returns `0` for `x0` (hard-wired zero).
- `update()` – after committing the synchronous write, forces `_memory[0] = 0`
  so `x0` stays zero even if a write was scheduled to it.

## Byte-Addressing Notes

`BlockMem` stores one `XLEN`-bit *cell* per address. The cores convert a byte
address to a word address with `>> 2` and compute the in-word byte offset with
`& 0b11`. Sub-word access (LB/LH/SB/SH) is expressed via the `byte_we` mask
passed to `BlockMem.write`. See `modules/README.md` for the `dmem_rd_port` /
`dmem_wr_port` formatting functions.
