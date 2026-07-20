# -------------import sim_base modules----------------
from sim_base.clock import Clock
from sim_base.mem.register import Register

# -------------import base risc_v modules-------------
from risc_v.modules.mem.dmem import DataMem
from risc_v.modules.mem.imem import InstrMem
from risc_v.modules.mem.reg_file import RegFile
from risc_v.modules.pc import PC

# -------------import pipeline stages-----------------
from risc_v.pipeline.stages.fetch import Fetch
from risc_v.pipeline.stages.decode import Decode
from risc_v.pipeline.stages.execute import Execute
from risc_v.pipeline.stages.mem import Memory
from risc_v.pipeline.stages.writeback import WriteBack

# -------------import local pipeline modules----------
import risc_v.pipeline.regs as regs
from risc_v.pipeline.hazard_detection_unit import Hazard_Detection_Unit


class Core:
    def __init__(self, clk: Clock, imem: InstrMem, dmem: DataMem, rst_reg: Register):
        self.clk = clk
        self.imem = imem
        self.dmem = dmem
        self.rst_reg = rst_reg

        # PC and Register File instantiation
        self.pc_inst = PC(rst_reg=self.rst_reg)
        self.clk.add_trigger(self.pc_inst.reg)

        self._rf_inst = RegFile()
        self.clk.add_trigger(self._rf_inst)

        # Pipeline Buffers
        self.buff_if_id = regs.IF_ID_Stage()
        self.buff_id_ex = regs.ID_EX_Stage()
        self.buff_ex_mem = regs.EX_MEM_Stage()
        self.buff_mem_wb = regs.MEM_WB_Stage()

        # Register all pipeline buffer registers as clock triggers
        for stage in (self.buff_if_id, self.buff_id_ex,
                      self.buff_ex_mem, self.buff_mem_wb):
            for reg in stage.get_registers():
                self.clk.add_trigger(reg)

        # Pipeline Stages Instantiation
        self.stage_fetch = Fetch(self.pc_inst,
                                 self.imem,
                                 self.buff_if_id)
        self.stage_decode = Decode(self._rf_inst,
                                   self.buff_if_id,
                                   self.buff_id_ex)
        self.stage_execute = Execute(self.buff_id_ex,
                                     self.buff_ex_mem)
        self.stage_memory = Memory(self.dmem,
                                   self.buff_ex_mem,
                                   self.buff_mem_wb)
        self.stage_writeback = WriteBack(self._rf_inst,
                                         self.buff_mem_wb,
                                         self.rst_reg)

        # Hazard Detection Unit
        self.hdu = Hazard_Detection_Unit(self.buff_if_id,
                                         self.buff_id_ex,
                                         self.buff_ex_mem,
                                         self.buff_mem_wb,
                                         self.stage_fetch,
                                         self.stage_decode,
                                         self.stage_execute,
                                         self.stage_memory,
                                         self.stage_writeback)

    def step(self) -> None:
        # Combinational stage updates
        self.stage_decode.update()
        self.stage_execute.update()
        self.stage_memory.update()
        self.stage_writeback.update()

        self.stage_fetch.update(
            jfexe=self.stage_execute.jfexe,
            jfid=self.stage_decode.jfid,
            alures=self.stage_execute.alures,
            imm_pc=self.stage_decode.imm_pc
        )

        self.hdu.update()

        # Commit all synchronous changes
        self.clk.tick()

    @property
    def reg_file(self) -> RegFile:
        return self._rf_inst

    def get_cur_pc(self) -> int:
        return self.pc_inst.read()
