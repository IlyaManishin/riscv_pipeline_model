# Hardware Simulation Core (`sim_base`)

This module serves as the fundamental cycle-accurate execution engine. It provides abstract interfaces and concrete implementations of digital hardware primitives to construct, simulate, and verify processor microarchitectures at the Register-Transfer Level (RTL).

---

## 📂 Directory Structure

```text
sim_base/
├── core/
│   ├── iclock.py          # Central clock distribution interface
│   ├── icomb.py           # Combinational logic block interface
│   └── itrigger.py        # Edge-triggered / sequential primitive interface
├── mem/
│   ├── base_mem.py        # Unified memory foundation class
│   ├── async_read_mem.py  # Asynchronous-read memory model
│   ├── multy_write_mem.py # Distributed memory model
│   ├── block_mem.py       # Synchronous Block RAM model with byte masking
│   └── register.py        # D-type flip-flop register model
└── clock.py               # Master clock management orchestration

```

---

## ⚙️ Architectural Mechanics & Clock Domains

The core utilizes a strict two-phase execution cycle within a single clock tick (`Clock.tick()`). This mechanism ensures race-free simulation and guarantees deterministic data propagation, mirroring physical hardware layouts.

### 1. Phase 1: Combinational Evaluation (`IComb`)

Evaluates purely combinational logic using the stable current state of sequential primitives to stage values into target components. This phase can also be triggered manually independent of the central clock orchestration loop.

### 2. Phase 2: Sequential State Commit (`ITrigger`)

Once combinational settling is complete, the clock issues an atomic state update command across all sequential structures. Temporary staged boundaries are latched into the active execution state.

---

## 🛠️ Primitive Component Specifications

### 1. Registers (`Register`)

Registers act as single-stage pipeline isolation boundaries.

* **`set(value)`**: Stages the incoming payload into an internal tracking buffer (`_next_value`).
* **`read()`**: Returns the locked `_current_value` computed from the previous clock cycle.
* **`update()`**: Latches `_next_value` into `_current_value` upon the active clock edge boundary.

### 2. Memory Architectures

#### Base Memory Foundation (`BaseMem`)

An abstract baseline structure derived from `ITrigger`. It manages uniform memory allocation constraints (cell counts, bit-width tracking), enforces strict address array boundary checking (`IndexError`), and exposes protected internal cell-access methods (`_read_cell` and `_write_cell`) inherited by concrete memory subclasses.

#### Asynchronous-Read Memory (`AsyncReadMem`)

Models distributed memory structures (e.g., Register Files, Lookup Tables). Reads are combinational and immediate. Writes are synchronized with the clock edge.

#### Synchronous Block RAM (`BlockMem`)

Models dedicated physical Block RAM blocks. To align with discrete programmatic model processing, it implements specialized architectural safeguards:

* **Single-Address Read Contention Constraint**: Reads evaluate combinationally to simplify data-bus scheduling. However, the simulation framework restricts queries to a single unique address per clock cycle. Attempting to update or alter the target read address pointer multiple times within one cycle triggers a simulation crash.
* **Byte-Level Write Enable Masking (`byte_we`)**: Supports granular sub-word updates. The component evaluates targeted byte fields inside the cell boundary while preserving adjacent unselected bytes.
* **Structural Write Conflict Interlocks**: Enforces a strict maximum limit of one write transaction per execution frame. Multiple concurrent write requests trigger immediate execution faults.
