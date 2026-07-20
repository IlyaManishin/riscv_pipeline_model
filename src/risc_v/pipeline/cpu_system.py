# -------------import sim_base modules----------------
from sim_base.clock import Clock
from sim_base.mem.register import Register

# -------------import base risc_v modules-------------
from risc_v.modules.mem.dmem import DataMem
from risc_v.modules.mem.imem import InstrMem
from risc_v.modules.mem.reg_file import RegFile
from risc_v.base.icpu_system import ICpuSystem
import risc_v.riscv_config as conf

# -------------import pipeline core-------------
from .cpu_core import Core


class CpuSystem(ICpuSystem):
    def __init__(self,
                 imem_addr_width: int = conf.IMEM_ADDR_BYTE_WIDTH - conf.BYTE_ADDR_WIDTH,
                 dmem_addr_width: int = conf.DMEM_ADDR_BYTE_WIDTH - conf.BYTE_ADDR_WIDTH):
        self.clk = Clock()

        # Memory instantiation
        self._imem = InstrMem(imem_addr_width)
        self._dmem = DataMem(dmem_addr_width)

        # Synchronous memory write on clock tick
        self.clk.add_trigger(self._imem)
        self.clk.add_trigger(self._dmem)

        # Asynchronous reset register
        self.rst_reg = Register(init_value=0)
        self.clk.add_trigger(self.rst_reg)

        # Core instantiation
        self.core = Core(clk=self.clk,
                         imem=self._imem,
                         dmem=self._dmem,
                         rst_reg=self.rst_reg)

    def step(self) -> None:
        self.core.step()

    @property
    def imem(self) -> InstrMem:
        return self._imem

    @property
    def dmem(self) -> DataMem:
        return self._dmem

    @property
    def reg_file(self) -> RegFile:
        return self.core.reg_file

    def get_cur_pc(self) -> int:
        return self.core.get_cur_pc()
