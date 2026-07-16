# `sim_base/` – Hardware Simulation Framework

A small, processor-agnostic framework that mimics RTL/hardware semantics in
Python. It is the foundation every `risc_v` component is built on. The key idea:
elements expose a combinational API (`set()`/`read()`) plus an `update()` method
that commits "next" values, and a `Clock` orchestrates when those commits
happen.

## Two Sub-packages

| Path | Document | Contents |
| --- | --- | --- |
| `core/` | [README](core/README.md) | Abstract interfaces: `IClock`, `ITrigger`, `IComb`. |
| `mem/` | [README](mem/README.md) | `Register`, `BaseMem`, `BlockMem`, `AsyncReadMem`, `MultiWriteMem`. |

## `clock.py` – `Clock`

Concrete implementation of `IClock`. It owns two ordered lists:

- **triggers** (`ITrigger`) – sequential state (registers, synchronous memories,
  pipeline buffers). `tick()` calls `update()` on each after combinational
  logic.
- **comb** (`IComb`) – pure combinational updates, also evaluated on `tick()`.

API: `add_trigger(trigger)`, `add_comb(comb)`, `tick()`. `tick()` runs all
`comb` updates first, then all `trigger` updates, modelling the synchronous
commit edge of a clock.

## Design Contract

- A sequential element stores a `current_value` and a `next_value`. Writes go
  to `next_value` (via `set()`); `update()` promotes `next → current`.
- This split lets datapath stages compute everything combinationally and then
  commit atomically, which is what makes the `risc_v` cores cycle-accurate and
  waveform-friendly.
