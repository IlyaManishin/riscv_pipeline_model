# `risc_v/pipeline/` – 5-Stage Pipelined Core

A classic 5-stage in-order pipeline (IF → ID → EX → MEM → WB) implementing
RV32I. It is the most complete core in the model and the primary target of the
architectural test suite (`tests/cpu/test_PL.py`).

## `cpu_system.py` – `CpuSystem` (top level)

Implements `ICpuSystem`. Responsibilities:

- Instantiates the synchronous `Clock` and binds all sequential elements to it
  as triggers: `InstrMem`, `DataMem`, reset `Register`, PC register, `RegFile`,
  and every pipeline-buffer register (via `regs.*Stage.get_triggers()`).
- Creates the four inter-stage pipeline buffers: `IF_ID_Stage`, `ID_EX_Stage`,
  `EX_MEM_Stage`, `MEM_WB_Stage` (defined in `regs.py`).
- Instantiates the five stages (`stages/`) and the `Hazard_Detection_Unit`.
- `step()` evaluates combinational stage logic first (Decode, Execute, Memory,
  WriteBack), then `Fetch.update(...)` passing branch/jump resolution signals
  (`jfexe`, `jfid`, `alures`, `imm_pc`) so the next PC is decided correctly,
  then runs `hdu.update()` for stall/flush control, and finally commits
  everything with `self.clk.tick()`.
- Exposes `imem`, `dmem`, `reg_file`, `get_cur_pc()`.

## `regs.py` – Pipeline Buffers

Dataclass-style register bundles between stages. Each is built from
`sim_base.mem.Register` elements and provides `get_triggers()` (for clock
binding), `stall()` (hold current values), and `flush()` (clear control/valid
bits to squash a stage).

- `IF_ID_Stage` – `pc`, `instr`, `valid`.
- `ID_EX_Stage` – `pc`, `rf_rd1`, `rf_rd2`, `imm`, `rs1`, `rs2`, `rd`,
  `alu_sel`, `shift_sel`, `a_sel`, `b_sel`, `wb_sel`, `reg_wr`, `dmem_sel`,
  `jfexe`, `alushift_sel`, `valid`.
- `EX_MEM_Stage` – `alu_out`, `rf_rd2`, `rd`, `wb_sel`, `reg_wr`, `dmem_sel`,
  `pc4`, `valid`.
- `MEM_WB_Stage` – `alu_out`, `dmem_data`, `rd`, `wb_sel`, `reg_wr`, `pc4`,
  `valid`.

## `hazard_detection_unit.py` – `Hazard_Detection_Unit`

Resolves pipeline hazards using the bound buffers and stage instances:

- **Control hazards** – JALR (`jf_exe` in Decode/Execute) flushes IF/ID (and
  ID/EX when resolved in Execute); branches/JAL (`jfid` in Decode) flush IF/ID.
- **RAW data hazards** – when an in-flight instruction in EX/MEM/WB will write
  a register that the current Decode reads (`rs1`/`rs2`), the unit stalls Fetch,
  stalls IF/ID, and flushes ID/EX until the producer reaches WB.
  *Note on Opcode-Based Optimization:* To prevent unnecessary stalls caused by 
  "ghost" register indices (where an instruction format exposes fields in `rs1`/`rs2` 
  but does not actually use them, such as in `JAL` or `LUI`), the unit evaluates the 
  current Decode instruction `opcode`. It dynamically generates `uses_rs1` and 
  `uses_rs2` validation flags, ensuring stalls are strictly triggered only when 
  the source registers are actively required by the decoded instruction type. 

The `update()` method is the single point where stall/flush control signals are
produced each cycle.

## Stages

See [`stages/README.md`](stages/README.md) for per-stage details.

## Notes

- The core is "microarchitecture-correct": each stage writes *next* buffer
  values combinationally and all updates commit on the clock tick, so a wave
  viewer sees realistic pipeline behaviour.
- `valid` bits let control transfers flush instructions without corrupting the
  architectural state.
