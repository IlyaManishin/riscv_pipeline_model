import risc_v.riscv_config as conf
import risc_v.pipeline.regs as regs
from risc_v.pipeline.stages.fetch import Fetch
from risc_v.pipeline.stages.decode import Decode
from risc_v.pipeline.stages.execute import Execute
from risc_v.pipeline.stages.mem import Memory
from risc_v.pipeline.stages.writeback import WriteBack


class Hazard_Detection_Unit:
    """
    Hazard Detection Unit (foundation).

    All pipeline buffers and stage instances are injected via the
    constructor. The conflict-resolution logic is intentionally left
    empty - implement it yourself in `update()` using the buffers and
    stages stored on `self`.

    Control signals you should produce each cycle (read by cpu_system /
    stages):
        self.stall     - 1 to stall the pipeline
        self.forward_a - forwarding selector for source operand A
        self.forward_b - forwarding selector for source operand B
    """

    def __init__(self,
                 buff_if_id:   regs.IF_ID_Stage,
                 buff_id_ex:   regs.ID_EX_Stage,
                 buff_ex_mem:  regs.EX_MEM_Stage,
                 buff_mem_wb:  regs.MEM_WB_Stage,
                 stage_fetch:      Fetch,
                 stage_decode:     Decode,
                 stage_execute:    Execute,
                 stage_memory:     Memory,
                 stage_writeback:  WriteBack):
        # Pipeline buffers
        self.buff_if_id = buff_if_id
        self.buff_id_ex = buff_id_ex
        self.buff_ex_mem = buff_ex_mem
        self.buff_mem_wb = buff_mem_wb

        # Pipeline stages
        self.stage_fetch = stage_fetch
        self.stage_decode = stage_decode
        self.stage_execute = stage_execute
        self.stage_memory = stage_memory
        self.stage_writeback = stage_writeback
        
        # --- Debug Flags ---
        self.is_id_ex_raw_hazard: bool = False
        self.is_id_mem_raw_hazard: bool = False
        self.is_id_wb_raw_hazard: bool = False

    def update(self) -> None:
        self.reset_debug_state()

        # ===== Control Hazards =====
        # jalr
        if self.stage_decode.id_controls.jf_exe:
            self.stage_fetch.stall()
            self.stage_fetch.flush()
        if self.stage_execute.jfexe:
            self.stage_fetch.flush()
            self.stage_decode.flush()

        # branch and jal
        if self.stage_decode.jfid:
            self.stage_fetch.flush()

        # ===== Data Hazards =====

        # RAW (Register after write hazard)
        opcode = self.stage_decode.instr.opcode >> 2
        uses_rs1 = opcode in (
            0b11001,  # JALR
            0b11000,  # Branch (BEQ, BNE, etc.)
            0b00000,  # Load
            0b01000,  # Store
            0b00100,  # Immediate ALU (ADDI, etc.)
            0b01100   # Register ALU (ADD, SUB, etc.)
        )

        uses_rs2 = opcode in (
            0b11000,  # Branch
            0b01000,  # Store
            0b01100   # Register ALU
        )

        # Decode-Execute Hazard
        if self.stage_execute.reg_wr and self.stage_execute.rd != 0 and (
            (uses_rs1 and self.stage_execute.rd == self.stage_decode.rs1) or
            (uses_rs2 and self.stage_execute.rd == self.stage_decode.rs2)
        ):
            self.is_id_ex_raw_hazard = True
            self.stage_fetch.stall()
            self.stage_decode.flush()

        # Decode-Memory Hazard
        if self.stage_memory.reg_wr and self.stage_memory.rd != 0 and (
            (uses_rs1 and self.stage_memory.rd == self.stage_decode.rs1) or
            (uses_rs2 and self.stage_memory.rd == self.stage_decode.rs2)
        ):
            self.is_id_mem_raw_hazard = True
            self.stage_fetch.stall()
            self.stage_decode.flush()

        # Decode-Writeback Hazard
        if self.stage_writeback.reg_wr and self.stage_writeback.rd != 0 and (
            (uses_rs1 and self.stage_writeback.rd == self.stage_decode.rs1) or
            (uses_rs2 and self.stage_writeback.rd == self.stage_decode.rs2)
        ):
            self.is_id_wb_raw_hazard = True
            self.stage_fetch.stall()
            self.stage_decode.flush()
            
    def reset_debug_state(self) -> None:
        self.is_id_ex_raw_hazard = False
        self.is_id_mem_raw_hazard = False
        self.is_id_wb_raw_hazard = False