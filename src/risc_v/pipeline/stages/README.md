```markdown
# `risc_v/pipeline/stages/` – Pipeline Stage Logic

Each stage is implemented as an autonomous processing unit. During `update()`, a stage reads the current combinational state from its **upstream input pipeline buffer** and writes the calculated next-state values into its **downstream output pipeline buffer**. All inter-stage register transfers commit synchronously on `Clock.tick()`.

## Architectural Rules & Memory Invariants

1. **Unidirectional Buffer Ownership (Producer/Consumer Architecture):**
   - Each stage exclusively **owns and writes to its downstream (output) pipeline buffer** (e.g., `Fetch` controls `IF_ID_Stage`, `Decode` controls `ID_EX_Stage`).
   - A stage only **reads from its upstream (input) pipeline buffer** filled by the preceding stage.
   - Pipeline register buffers do not drive control flow autonomously; pipeline control actions (`stall`, `flush`) are strictly encapsulated within and exposed by the managing stage interface.

2. **Strict Type Annotations & Clean State Initialization:**
   - Structural stage attributes are clearly compartmentalized into **Dependencies**, **Control Signals**, and **Data Path** fields.

---

## `fetch.py` – `Fetch` (IF)

- **Input Interfacing:** `PC`, `InstrMem`.
- **Managed Output Buffer:** `IF_ID_Stage` (upstream producer).
- `update(jfexe, jfid, alures, imm_pc)`: Fetches instruction at the current PC into `IF_ID.instr`, asserts `IF_ID.valid = True`, and updates internal data path state. Resolves next-PC selection via branch/jump signals (`jfid` or `jfexe`).
- **Control Interface:**
  - `stall()`: Holds current PC state and delegates pipeline register hold to `IF_ID.stall()`.
  - `flush()`: Delegates instruction squashing to `IF_ID.flush()`.

## `decode.py` – `Decode` (ID)

- **Input Interfacing:** `RegFile`, `IF_ID_Stage` (downstream consumer).
- **Managed Output Buffer:** `ID_EX_Stage` (upstream producer).
- `update()`: Decodes `IF_ID.instr` via `Instruction_Decoder`, generates immediates via `ImmGen`, evaluates branch conditions via `BranchUnit`, and combinationally populates all decoded execution signals into `ID_EX_Stage`.
- **Control Interface:**
  - `stall()`: Delegates pipeline hold to `ID_EX.stall()`.
  - `flush()`: Squashes decoded control signals via `ID_EX.flush()`.

## `execute.py` – `Execute` (EX)

- **Input Interfacing:** `ID_EX_Stage` (downstream consumer).
- **Managed Output Buffer:** `EX_MEM_Stage` (upstream producer).
- `update()`: Selects ALU/Shifter operands based on control vectors, executes arithmetic/logic and shift operations, and writes the execution context (`alu_out`, `rf_rd2`, `rd`, control flags) into `EX_MEM_Stage`.

## `mem.py` – `Memory` (MEM)

- **Input Interfacing:** `DataMem`, `EX_MEM_Stage` (downstream consumer).
- **Managed Output Buffer:** `MEM_WB_Stage` (upstream producer).
- `update()`: Reconstructs memory transaction parameters via `DMem_sel`, executes byte/halfword/word store/load routines via `dmem_wr_port` / `dmem_rd_port`, and passes result vectors down to `MEM_WB_Stage`.

## `writeback.py` – `WriteBack` (WB)

- **Input Interfacing:** `RegFile`, `MEM_WB_Stage` (downstream consumer), reset `Register`.
- **Managed Output Buffer:** None (Architectural State Commit Stage).
- `update()`: Selects write-back payload source via `WB_sel_t` and commits write payload to `RegFile` at index `rd` when `reg_wr` is active and hardware reset is inactive (`rf_we3`).

---

## Pipeline Control & Hazard Detection Interface

The `Hazard_Detection_Unit` resolves hazards purely through high-level stage control interfaces (`Fetch`, `Decode`) rather than directly manipulating raw pipeline buffers.

```text
               Control / Flush / Stall Trigger Path
  ┌─────────────────────────────────────────────────────────────┐
  │                   Hazard Detection Unit                     │
  └───────┬──────────────────────┬──────────────────────┬───────┘
          │ (stall/flush)        │ (flush)              │ (debug signals)
          ▼                      ▼                      ▼
     [ Fetch ]              [ Decode ]             [ Debug Flags ]
         │                      │                  • is_id_ex_raw_hazard
         │ (writes next)        │ (writes next)    • is_id_mem_raw_hazard
         ▼                      ▼                  • is_id_wb_raw_hazard
    [ IF/ID Reg ]          [ ID/EX Reg ]

```

* **Debug Interface:** The hazard unit provides runtime diagnostic flags (`is_id_ex_raw_hazard`, `is_id_mem_raw_hazard`, `is_id_wb_raw_hazard`), which are automatically cleared via `reset_debug_state()` at the start of each evaluation cycle.

```