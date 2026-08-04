# `risc_v/single_cycle/` – Single-Cycle Core

A single-cycle RV32I implementation: every instruction completes in exactly one
clock edge. It is simpler than the pipelined core and is the second core
exercised by the architectural test suite (`tests/cpu/test_SC.py`).

## `cpu_system.py` – `CpuSystem` (top level)

Implements `ICpuSystem`. Responsibilities:

- Creates the synchronous `Clock` and binds `InstrMem`, `DataMem`, reset
  `Register`, and the core's PC/RegFile to it as triggers.
- Instantiates `Core` (the datapath, defined in `cpu_core.py`) with the clock
  and reset register.
- `step()` runs the full instruction in one edge:
  1. `Core.get_imem_addr()` → read instruction from `InstrMem`.
  2. `Core.dec_exec_alu(instr)` – decode + register read + ALU/shifter +
     compute DMEM address and store write data (combinational).
  3. Perform the (byte-masked) `DataMem` write if `byte_we != 0`, then read the
     word back.
  4. `Core.write_back_comb(data_to_cpu)` – write-back mux, RegFile write, PC
     update.
  5. `Clock.tick()` commits all synchronous changes.
- Exposes `imem`, `dmem`, `reg_file` (delegates to `Core.rf_inst`),
  `get_cur_pc()` (returns `Core.pc`).

## `cpu_core.py` – `Core` (datapath)

Holds the combinational state of the datapath (PC, decoded fields, register
read values, ALU/shifter results, DMEM interface wires) and implements the
per-instruction logic:

- `get_imem_addr()` – returns the PC used for instruction fetch.
- `dec_exec_alu(instr_raw) -> DMemAccessData` – decodes the instruction,
  reads `rs1`/`rs2`, resolves branches via `BranchUnit.compare`, generates the
  immediate via `ImmGen`, computes the ALU/shifter results, and formats the
  store access (address, `wdata`, `byte_we`) through `dmem_wr_port`.
  Returns a `DMemAccessData` dataclass (`addr`, `wdata`, `byte_we`).
- `write_back_comb(dmem_data_in)` – formats the load result via `dmem_rd_port`,
  selects the write-back source (`WB_sel_t`), writes `rd` in the RegFile (gated
  by reset), and updates the PC (`set_pc`) based on `pc_sel`.

Unlike the pipeline core, there are no inter-stage buffers or hazard unit; the
single-cycle core trades throughput for implementation simplicity.
