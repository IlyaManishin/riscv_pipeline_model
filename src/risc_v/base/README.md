# `risc_v/base/` – CPU System Interface

Defines the abstract contract shared by every processor core implementation in
the model. It exists so that verification code (in `tests/`) can drive any core
– single-cycle or pipelined – through an identical, microarchitecture-agnostic
API.

## `icpu_system.py`

`ICpuSystem` (abstract base class) specifies the minimum surface a runnable CPU
must expose:

| Member | Kind | Purpose |
| --- | --- | --- |
| `imem` | property → `InstrMem` | Instruction memory (load programs, read instructions). |
| `dmem` | property → `DataMem` | Data memory (load data, run loads/stores). |
| `reg_file` | property → `RegFile` | General-purpose register file (read state for checks/traces). |
| `step()` | method | Advance the processor by **one clock edge** (one instruction for single-cycle, one stage advance for pipelined). |
| `get_cur_pc()` | method | Return the current program counter (used by tracers). |

Both `risc_v/single_cycle/cpu_system.py:CpuSystem` and
`risc_v/pipeline/cpu_system.py:CpuSystem` subclass `ICpuSystem`. Because the
test runner in `tests/cpu/runner.py` is typed against `ICpuSystem`, the exact
same benchmark harness runs against both microarchitectures.
