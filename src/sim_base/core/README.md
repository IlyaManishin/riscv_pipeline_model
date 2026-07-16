# `sim_base/core/` – Clock & Update Interfaces

Abstract base classes defining the simulation update contract. They are
consumed by `sim_base/clock.py:Clock` and implemented by the memory/register
primitives in `sim_base/mem/`.

## `itrigger.py` – `ITrigger`

Interface for **sequential** (clocked) elements.

- `update()` – abstract; commit the previously scheduled "next" value to the
  current state. Implemented by `Register` and all memory classes.

## `icomb.py` – `IComb`

Interface for **combinational** elements.

- `update()` – abstract; recompute outputs from current inputs. Evaluated by
  `Clock.tick()` before triggers, for purely combinational blocks.

## `iclock.py` – `IClock`

Interface for the simulation clock/scheduler.

- `add_trigger(trigger: ITrigger)` – register a sequential element.
- `add_comb(comb: IComb)` – register a combinational element.
- `tick()` – advance one clock edge (run `comb` then `trigger` updates).

`Clock` (in `sim_base/clock.py`) is the concrete implementation. These ABCs
keep the framework decoupled from the RISC-V model and make it reusable for
other simulated hardware.
