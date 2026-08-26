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

        # ============ Debug Flags ==============
        # Control Hazards
        self.jfid_hazard: bool = False
        self.jfexe_hazard: bool = False

        # Data Hazards
        self.id_ex_raw_hazard: bool = False
        self.id_mem_raw_hazard: bool = False
        self.id_wb_raw_hazard: bool = False
        self.raw_hazard: bool = False

    def update(self) -> None:
        self.reset_debug_state()

        # ===== RAW Hazard Detection (rs1/rs2 usage per opcode) =====
        ex_reg_wr = self.buff_id_ex.reg_wr.read()
        ex_rd = self.buff_id_ex.rd.read()

        mem_reg_wr = self.buff_ex_mem.reg_wr.read()
        mem_rd = self.buff_ex_mem.rd.read()

        wb_reg_wr = self.buff_mem_wb.reg_wr.read()
        wb_rd = self.buff_mem_wb.rd.read()

        is_ex_hazard = ex_reg_wr and ex_rd != 0 and (
            ex_rd == self.stage_decode.rs1 or
            ex_rd == self.stage_decode.rs2
        )

        is_mem_hazard = mem_reg_wr and mem_rd != 0 and (
            mem_rd == self.stage_decode.rs1 or
            mem_rd == self.stage_decode.rs2
        )

        is_wb_hazard = wb_reg_wr and wb_rd != 0 and (
            wb_rd == self.stage_decode.rs1 or
            wb_rd == self.stage_decode.rs2
        )

        # ===== Control Hazards (branch / jump redirect) =====

        # jfexe_M: JALR target was resolved in Execute
        jfexe_M_val = self.stage_execute.jfexe_M.read()
        if jfexe_M_val:
            self.jfexe_hazard = True
            self.stage_decode.flush()
            self.stage_execute.flush()

        # jfid_E: branch/jal outcome was resolved in Decode
        jfid_E_val = self.stage_decode.jfid_E.read()
        if jfid_E_val:
            self.jfid_hazard = True
            self.stage_decode.flush()

        # jfid_E and jfexe_M ignore RAW hazards because decode stage already has been flushed
        is_control_hazard = jfid_E_val or jfexe_M_val
        if is_control_hazard:
            return

        # ===== Data Hazards (RAW) =====
        # Set debug wires
        self.id_ex_raw_hazard = is_ex_hazard
        self.id_mem_raw_hazard = is_mem_hazard
        self.id_wb_raw_hazard = is_wb_hazard
        self.raw_hazard = is_ex_hazard or is_mem_hazard or is_wb_hazard
        
        # Pipeline stall
        if is_ex_hazard or is_mem_hazard or is_wb_hazard:
            self.stage_fetch.pc_stall()
            self.stage_fetch.stall()
            self.stage_decode.flush()

    def reset_debug_state(self) -> None:
        self.jfid_hazard = False
        self.jfexe_hazard = False
        self.id_ex_raw_hazard = False
        self.id_mem_raw_hazard = False
        self.id_wb_raw_hazard = False
        self.raw_hazard = False
