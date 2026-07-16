# `risc_v/pipeline/stages/` – Pipeline Stage Logic

Each file contains one stage class. A stage reads the *current* values from its
input pipeline buffer(s) and writes the *next* values into its output buffer(s)
during `update()`. All writes are committed when the parent `CpuSystem` calls
`Clock.tick()`.

The pipeline registers are defined in [`../regs.py`](../regs.py); the shared
control dataclasses/enums are in `risc_v/riscv_config.py`.

## `fetch.py` – `Fetch` (IF)

- Inputs: `PC`, `InstrMem`, `IF_ID_Stage`.
- `update(jfexe, jfid, alures, imm_pc)` reads the instruction at the current PC
  into `IF_ID.instr`, sets `IF_ID.pc` and `IF_ID.valid=1`.
- Next-PC selection: if `jfid` (branch/JAL resolved in Decode) jump to
  `imm_pc`; elif `jfexe` (JALR resolved in Execute) jump to `alures`; else
  PC+4. Uses `PC.set_pc`.
- `stall()` holds the PC for one cycle (redirects PC to its current value).

## `decode.py` – `Decode` (ID)

- Inputs: `RegFile`, `IF_ID_Stage`, `ID_EX_Stage`.
- `update()` decodes `IF_ID.instr` via `Instruction_Decoder` (two passes, with
  `BranchUnit` comparison for branch resolution), generates the immediate via
  `ImmGen`, reads `rs1`/`rs2`, and writes every decoded control field into
  `ID_EX_Stage`.
- Computes `imm_pc = pc + imm` and the `jfid` (taken-branch/JAL) signal used by
  Fetch. Propagates `valid` from IF/ID.

## `execute.py` – `Execute` (EX)

- Inputs: `ID_EX_Stage`, `EX_MEM_Stage`.
- `update()` selects ALU operands (`a_sel`/`b_sel` choose register vs PC/imm),
  runs `Alu.execute`, runs `Shifter.shift` for shift ops, and chooses the ALU
  vs shifter result via `alushift_sel`.
- Writes `alu_out`, `rf_rd2` (store data), `rd`, `wb_sel`, `reg_wr`,
  `dmem_sel`, `pc4`, and the `jfexe` (JALR) flag into `EX_MEM_Stage`.

## `mem.py` – `Memory` (MEM)

- Inputs: `DataMem`, `EX_MEM_Stage`, `MEM_WB_Stage`.
- `update()` reconstructs the `DMem_sel` from `dmem_sel`, computes the byte
  offset, formats the store word via `dmem_wr_port`, performs the (byte-masked)
  write, reads the word back, formats the load result via `dmem_rd_port`, and
  forwards `alu_out`, `dmem_data`, `rd`, `wb_sel`, `reg_wr`, `pc4` to
  `MEM_WB_Stage`.

## `writeback.py` – `WriteBack` (WB)

- Inputs: `RegFile`, `MEM_WB_Stage`, reset `Register`.
- `update()` selects the write-back source via `WB_sel_t`
  (PC4_OUT / ALU_OUT / SHIFTER_OUT / DMEM_OUT), and writes `rd` in `RegFile`
  when `reg_wr` is set **and** reset is not active (`rf_we3` gate).

## Data Flow Summary

```text
      PC ─┐
          ▼
   [ Fetch ]──IF/ID──▶[ Decode ]──ID/EX──▶[ Execute ]──EX/MEM──▶[ Memory ]──MEM/WB──▶[ WriteBack ]
          ▲                                   │                  │                     │
          └──── next-PC (jfid/jfexe) ──────────┘                  ▼                     ▼
                                                     DataMem ◀──▶ RegFile
```
