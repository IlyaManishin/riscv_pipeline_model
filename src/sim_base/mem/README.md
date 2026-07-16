# `sim_base/mem/` – Memory & Register Primitives

Low-level storage primitives shared by the RISC-V model (`risc_v/modules/mem/`).
They implement the `ITrigger`/`IComb` contracts from `sim_base/core/` and model
synchronous (clocked) writes with combinational reads, plus single-cycle access
conflict detection that is useful for verification.

## `register.py` – `Register`

The fundamental sequential element (implements `ITrigger`).

- `set(next_value)` – schedule the next value.
- `update()` – commit: `current = next`.
- `read()` – return current value.
- Writes are deferred: nothing changes until `update()` (typically driven by
  `Clock.tick()`). Used for the PC, pipeline buffers, and the reset register.

## `base_mem.py` – `BaseMem`

Abstract base (implements `ITrigger`) holding the raw `_memory` list, `_size`,
`_cell_size`, and `_cell_mask`. Provides address validation and cell
read/write helpers, and declares the abstract `read` / `write` / `update`
interface used by all concrete memories.

## `block_mem.py` – `BlockMem`

Cell-addressed, **synchronous**, byte-maskable block memory (subclass of
`BaseMem`). This is what `InstrMem` and `DataMem` derive from.

- `read(addr)` – combinational read; detects **multiple distinct reads in one
  cycle** and raises `RuntimeError` (single-read-per-cycle contract).
- `write(addr, value, byte_we=None)` – deferred write. Detects **multiple
  writes in one cycle** (`RuntimeError`). Supports sub-word writes via
  `byte_we` masking (byte/halfword/word). `byte_we == 0` is a no-op.
- `update()` – clears the read-conflict flag and commits the pending write.
- `addr_overflow` – wraps addresses by the address mask (used by the RISC-V
  memories). `get_addr_width()` exposes the cell-address width.

## `async_read_mem.py` – `AsyncReadMem`

Asynchronous-read, synchronous-write memory (subclass of `BaseMem`). This is
what `RegFile` derives from.

- `read(address)` – combinational, **no single-cycle read restriction** (many
  reads allowed).
- `write(address, value)` – deferred; one write per cycle (`RuntimeError` on
  conflict).
- `update()` – commits the pending write.

## `multi_write_mem.py` – `MultiWriteMem`

Permissive variant (subclass of `BaseMem`) that **accumulates multiple writes
per cycle** in `_transactions` and flushes them all on `update()`. Useful for
modelling memories that allow several simultaneous writes (not used by the
current RISC-V cores, but available as a primitive).

## Byte-Addressing Convention

All block memories store one `XLEN`-bit *cell* per address. Sub-word access is
expressed with a `byte_we` bitmask (4 bits for a 32-bit cell). The RISC-V
`dmem_rd_port` / `dmem_wr_port` helpers translate between byte addresses and
these masks.
