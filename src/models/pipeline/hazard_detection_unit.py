# -------------import pipeline stages-----------------
from .stages.fetch import Fetch
from .stages.decode import Decode
from .stages.execute import Execute
from .stages.memory import Memory
from .stages.writeback import WriteBack

from . import regs


class Hazard_Detection_Unit:
    """
    Hazard Detection Unit.

    Mirrors hazard_detection_unit.sv exactly:
      * Control hazards are resolved using the DELAYED redirect signals
        (stage_execute.jfexe_M and stage_decode.jfid_E) - never the
        immediate, same-cycle stage_execute.jfexe / stage_decode.jfid.
        Both only ever flush the ID/EX register (squash Decode); the PC
        redirect itself is handled entirely inside Fetch, not here.
      * RAW hazards stall the fetch/IF-ID stage and flush ID/EX, exactly
        like stall_pc/stall_if_id/flush_id_ex in the RTL.
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
        self.is_raw_hazard: bool = False

    def update(self) -> None:
        self.reset_debug_state()

        # ===== RAW Hazard Detection (rs1/rs2 usage per opcode) =====
        ex_reg_wr = self.buff_ex_mem.reg_wr.read()
        ex_rd = self.buff_ex_mem.rd.read()

        mem_reg_wr = self.buff_mem_wb.reg_wr.read()
        mem_rd = self.buff_mem_wb.rd.read()

        wb_reg_wr = self.stage_writeback.reg_wr
        wb_rd = self.stage_writeback.rd

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

        is_ex_hazard = ex_reg_wr and ex_rd != 0 and (
            (uses_rs1 and ex_rd == self.stage_decode.rs1) or
            (uses_rs2 and ex_rd == self.stage_decode.rs2)
        )
        is_mem_hazard = mem_reg_wr and mem_rd != 0 and (
            (uses_rs1 and mem_rd == self.stage_decode.rs1) or
            (uses_rs2 and mem_rd == self.stage_decode.rs2)
        )
        is_wb_hazard = wb_reg_wr and wb_rd != 0 and (
            (uses_rs1 and wb_rd == self.stage_decode.rs1) or
            (uses_rs2 and wb_rd == self.stage_decode.rs2)
        )

        self.is_id_ex_raw_hazard = is_ex_hazard
        self.is_id_mem_raw_hazard = is_mem_hazard
        self.is_id_wb_raw_hazard = is_wb_hazard
        self.is_raw_hazard = is_ex_hazard or is_mem_hazard or is_wb_hazard

        # ===== Control Hazards (branch / jump redirect) =====

        # jfexe_M: JALR target was resolved in Execute and is now
        if self.stage_execute.jfexe_M.read():
            self.stage_decode.flush()

        # jfid_E: branch/jal outcome was resolved in Decode and is now
        if self.stage_decode.jfid_E.read():
            self.stage_decode.flush()

        # ===== Data Hazards (RAW) =====
        if is_ex_hazard or is_mem_hazard or is_wb_hazard:
            self.stage_fetch.pc_stall()
            self.stage_fetch.stall()
            self.stage_decode.flush()

    def reset_debug_state(self) -> None:
        self.is_id_ex_raw_hazard = False
        self.is_id_mem_raw_hazard = False
        self.is_id_wb_raw_hazard = False
        self.is_raw_hazard = False
