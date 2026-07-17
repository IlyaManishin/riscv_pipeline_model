# `risc_v/modules/` – Datapath Building Blocks

Combinational and memory components shared by all processor cores. With the
exception of the memory components (which subclass `sim_base` memories), the
datapath blocks are implemented as classes with **static methods** so they can
be invoked functionally without holding instance state.

## Combinational Datapath Modules

| File | Class / function | Description |
| --- | --- | --- |
| `alu.py` | `Alu.execute(sel, a, b)` | Arithmetic Logic Unit. Implements ADD, SUB, AND, OR, XOR, SLT (signed), SLTU (unsigned), JALR (`(a+b)&~1`), LUI (`b`). Inputs/outputs masked to `XLEN`. |
| `shifter.py` | `Shifter.shift(data, shamt, sel)` | Barrel shifter. `SLL` (logical left), `SRL` (logical right), `SRA` (arithmetic right with sign extension), `ANY` (→0). |
| `branch_unit.py` | `BranchUnit.compare(rd1, rd2, br_un)` | Returns `(br_eq, br_lt)`. Signed compare when `br_un=False`, unsigned when `br_un=True`. |
| `immgen.py` | `ImmGen.generate(instr, imm_type)` | Immediate generator. Decodes I/S/B/U/J immediates from a 32-bit `Instruction`, with correct sign extension. Returns `0` for unsupported/`ANY`. |
| `decode.py` | `Instruction_Decoder.decode(instr, br_eq=False, br_lt=False)` | The control unit. Maps opcode/funct3/funct7 to an `Id_controls_out` dataclass. Two-pass: branch resolution (`br_eq`/`br_lt`) is supplied on the second call to choose taken/not-taken control signals. Decodes the full RV32I set including LUI, AUIPC, JAL, JALR (`jf_exe=1`), branches, loads, stores, ALU-immediate and ALU-register ops, FENCE and ECALL/EBREAK (mapped to NOP). Unknown opcodes return `illegal=1`. |
| `pc.py` | `PC` | Program counter wrapper around a `sim_base` `Register`. `read()`, `set_pc(br_taken, pc_br)` (reset → start addr; branch taken → `pc_br`; else PC+4, masked to `XLEN`), and `stall()` to hold the PC for one cycle. |

## Data-Memory Port Functions

These pure functions format/extract sub-word data for load/store operations
(the `byte_we` byte-write-enable convention comes from `sim_base.mem.BlockMem`).

| File | Function | Description |
| --- | --- | --- |
| `dmem_rd_port.py` | `dmem_rd_port(dmem_raw, byte_addr, funct3)` | Read port. Given a full 32-bit memory word and a byte offset, returns LB/LH/LW/LBU/LHU data with correct sign/zero extension. |
| `dmem_wr_port.py` | `dmem_wr_port(data, byte_offset, funct3)` | Write port. Returns `(write_data, byte_we)` for SB/SH/SW (broadcast/merge for sub-word stores). Raises on unsupported `funct3`. |

## Memory Components

The memory-backed modules live in the `mem/` sub-package – see
[`mem/README.md`](mem/README.md).

## How Cores Use These Modules

- The **pipeline** core wires each module into a stage (see
  [`pipeline/stages/`](../pipeline/stages/README.md)).
- The **single-cycle** core calls `Instruction_Decoder`, `ImmGen`,
  `BranchUnit`, `Alu`, `Shifter`, and the `dmem_*_port` helpers inside
  `single_cycle/cpu_core.py:Core.dec_exec_alu` / `write_back_comb`.
- `riscv_config.py`'s `DMem_sel` helpers bridge `funct3` to the port functions.
