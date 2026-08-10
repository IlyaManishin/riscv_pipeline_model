# -------------import sim_base modules----------------
from sim_base.clock import Clock
from sim_base.mem.register import Register

# -------------import base risc_v modules-------------
from risc_v.mem.pl.dmem import DataMem
from risc_v.mem.pl.imem import InstrMem
from risc_v.mem.reg_file import RegFile
from risc_v.modules.pc import PC

# -------------import pipeline stages-----------------
from .stages.fetch import Fetch
from .stages.decode import Decode
from .stages.execute import Execute
from .stages.memory import Memory
from .stages.writeback import WriteBack

# -------------import local pipeline modules----------
from . import regs
from .hazard_detection_unit import Hazard_Detection_Unit


class Core:
    def __init__(self, clk: Clock, imem: InstrMem, dmem: DataMem, rst_reg: Register[bool]):
        self.clk = clk
        self.imem = imem
        self.dmem = dmem
        self.rst_reg = rst_reg

        # PC and Register File instantiation
        self.pc_inst = PC(rst_reg=self.rst_reg)
        self.clk.add_trigger(self.pc_inst.reg)

        self._rf_inst = RegFile()
        self.clk.add_trigger(self._rf_inst)

        # Control-hazard jump registers (ID/EX and EX/MEM "extra" flops)
        self.jfid_E: Register[bool] = Register(False)
        self.jfpc_E: Register[int] = Register(0)
        self.jfexe_M: Register[bool] = Register(False)
        self.jfpc_M: Register[int] = Register(0)

        for reg in (self.jfid_E, self.jfpc_E, self.jfexe_M, self.jfpc_M):
            self.clk.add_trigger(reg)

        # Pipeline Buffers
        self.buff_if_id = regs.IF_ID_Stage(imem)
        self.buff_id_ex = regs.ID_EX_Stage()
        self.buff_ex_mem = regs.EX_MEM_Stage()
        self.buff_mem_wb = regs.MEM_WB_Stage(dmem)

        # Register all pipeline buffer registers as clock triggers
        for stage in (self.buff_if_id, self.buff_id_ex,
                      self.buff_ex_mem, self.buff_mem_wb):
            for reg in stage.get_registers():
                self.clk.add_trigger(reg)

        self.init_modules()

    def init_modules(self) -> None:
        # Pipeline Stages Instantiation
        self.stage_fetch = Fetch(self.pc_inst,
                                 self.imem,
                                 self.buff_if_id,
                                 self.jfid_E,
                                 self.jfpc_E,
                                 self.jfexe_M,
                                 self.jfpc_M)
        self.stage_decode = Decode(self._rf_inst,
                                   self.buff_if_id,
                                   self.buff_id_ex,
                                   self.jfid_E,
                                   self.jfpc_E)
        self.stage_execute = Execute(self.buff_id_ex,
                                     self.buff_ex_mem,
                                     self.jfexe_M,
                                     self.jfpc_M)
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
        self.stage_fetch.update()
        self.stage_decode.update()
        self.stage_execute.update()
        self.stage_memory.update()
        self.stage_writeback.update()

        self.hdu.update()

        # Commit all synchronous changes
        self.clk.tick()

    @property
    def reg_file(self) -> RegFile:
        return self._rf_inst

    def get_cur_pc(self) -> int:
        return self.stage_fetch.pc_next
