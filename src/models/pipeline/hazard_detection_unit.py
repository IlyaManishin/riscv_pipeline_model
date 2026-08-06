# -------------import pipeline stages-----------------
from .stages.fetch import Fetch
from .stages.decode import Decode
from .stages.execute import Execute
from .stages.memory import Memory
from .stages.writeback import WriteBack

from . import regs


class Hazard_Detection_Unit:
    """
    Mirrors hazard_detection_unit.sv:
      * control hazards use the delayed jfexe_M/jfid_E registers and only
        ever flush Decode - PC redirect itself lives inside Fetch;
      * flush_if_id is never asserted in the RTL, so Fetch is never flushed
        here, only stalled on a RAW hazard.
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

        # ===== RAW Hazard Detection =====
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

        is_ex_hazard = self.stage_execute.reg_wr and self.stage_execute.rd != 0 and (
            (uses_rs1 and self.stage_execute.rd == self.stage_decode.rs1) or
            (uses_rs2 and self.stage_execute.rd == self.stage_decode.rs2)
        )
        is_mem_hazard = self.stage_memory.reg_wr and self.stage_memory.rd != 0 and (
            (uses_rs1 and self.stage_memory.rd == self.stage_decode.rs1) or
            (uses_rs2 and self.stage_memory.rd == self.stage_decode.rs2)
        )
        is_wb_hazard = self.stage_writeback.reg_wr and self.stage_writeback.rd != 0 and (
            (uses_rs1 and self.stage_writeback.rd == self.stage_decode.rs1) or
            (uses_rs2 and self.stage_writeback.rd == self.stage_decode.rs2)
        )

        self.is_id_ex_raw_hazard = is_ex_hazard
        self.is_id_mem_raw_hazard = is_mem_hazard
        self.is_id_wb_raw_hazard = is_wb_hazard

        # ===== Control Hazards =====
        if self.stage_execute.jfexe_M.read():
            self.stage_decode.flush()

        if self.stage_decode.jfid_E.read():
            self.stage_decode.flush()

        # ===== Data Hazards (RAW) =====
        if is_ex_hazard or is_mem_hazard or is_wb_hazard:
            self.stage_fetch.stall()
            self.stage_decode.flush()

    def reset_debug_state(self) -> None:
        self.is_id_ex_raw_hazard = False
        self.is_id_mem_raw_hazard = False
        self.is_id_wb_raw_hazard = False
