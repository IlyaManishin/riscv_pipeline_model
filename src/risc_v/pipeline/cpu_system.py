import risc_v.riscv_config as conf
import risc_v.pipeline.regs as regs
from sim_base.clock import Clock
from sim_base.mem.register import Register
from risc_v.modules.mem.dmem import DataMem
from risc_v.modules.mem.imem import InstrMem
from risc_v.modules.mem.reg_file import RegFile
from risc_v.modules.pc import PC

from risc_v.pipeline.stages.fetch import Fetch
from risc_v.pipeline.stages.decode import Decode
from risc_v.pipeline.stages.execute import Execute
from risc_v.pipeline.stages.mem import Memory
from risc_v.pipeline.stages.writeback import WriteBack

from risc_v.pipeline.hazard_detection_unit import Hazard_Detection_Unit

from risc_v.base.icpu_system import ICpuSystem


class CpuSystem(ICpuSystem):
    def __init__(self,
                 imem_addr_width: int = conf.IMEM_ADDR_BYTE_WIDTH - conf.BYTE_ADDR_WIDTH,
                 dmem_addr_width: int = conf.DMEM_ADDR_BYTE_WIDTH - conf.BYTE_ADDR_WIDTH):
        self.clk = Clock()

        # Memory instantiation
        self._imem = InstrMem(imem_addr_width)
        self._dmem = DataMem(dmem_addr_width)

        # Synchrone memory write on clock tick
        self.clk.add_trigger(self._imem)
        self.clk.add_trigger(self._dmem)

        # Asynchronous reset register
        self.rst_reg = Register(init_value=0)
        self.clk.add_trigger(self.rst_reg)

        self.pc_inst = PC(rst_reg=self.rst_reg)
        self.clk.add_trigger(self.pc_inst.reg)

        self._rf_inst = RegFile()
        self.clk.add_trigger(self._rf_inst)

        self.buff_if_id = regs.IF_ID_Stage()
        self.buff_id_ex = regs.ID_EX_Stage()
        self.buff_ex_mem = regs.EX_MEM_Stage()
        self.buff_mem_wb = regs.MEM_WB_Stage()

        # Register all pipeline buffer registers as clock triggers
        for stage in (self.buff_if_id, self.buff_id_ex,
                      self.buff_ex_mem, self.buff_mem_wb):
            for reg in stage.get_triggers():
                self.clk.add_trigger(reg)

        self.stage_fetch = Fetch(self.pc_inst,
                                 self._imem,
                                 self.buff_if_id)
        self.stage_decode = Decode(self._rf_inst,
                                   self.buff_if_id,
                                   self.buff_id_ex)
        self.stage_execute = Execute(self.buff_id_ex,
                                     self.buff_ex_mem)
        self.stage_memory = Memory(self._dmem,
                                   self.buff_ex_mem,
                                   self.buff_mem_wb)
        self.stage_writeback = WriteBack(self._rf_inst,
                                         self.buff_mem_wb,
                                         self.rst_reg)
        
        self.hdu = Hazard_Detection_Unit(self.buff_if_id,
                                         self.buff_id_ex,
                                         self.buff_ex_mem,
                                         self.buff_mem_wb,
                                         self.stage_fetch,
                                         self.stage_decode,
                                         self.stage_execute,
                                         self.stage_memory,
                                         self.stage_writeback)

    def step(self):
        # Combinational stage updates (each reads current buffer values and
        # writes the next values; everything is committed on the clock tick).
        # Decode and Execute are evaluated first so their branch/jump
        # resolution signals can drive the next PC in the Fetch stage.
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

        # Commit all synchronous changes (Clock Tick)
        self.clk.tick()

    @property
    def imem(self) -> InstrMem:
        return self._imem

    @property
    def dmem(self) -> DataMem:
        return self._dmem

    @property
    def reg_file(self) -> RegFile:
        return self._rf_inst
