from sim_base.clock import Clock
from sim_base.mem.register import Register

from risc_v.base.icpu_system import ICpuSystem
from risc_v import riscv_config as conf
from risc_v.modules.mem.dmem import DataMem
from risc_v.modules.mem.imem import InstrMem
from risc_v.modules.mem.reg_file import RegFile
from .cpu_core import Core


# =========================================================================
# SYSTEM TOP-LEVEL CLASS DEFINITION
# =========================================================================
class CpuSystem(ICpuSystem):

    def __init__(self,
                 imem_addr_width: int = conf.IMEM_ADDR_BYTE_WIDTH - conf.BYTE_ADDR_WIDTH,
                 dmem_addr_width: int = conf.DMEM_ADDR_BYTE_WIDTH - conf.BYTE_ADDR_WIDTH):

        self._clk = Clock()

        # Memory instantiation
        self._imem = InstrMem(imem_addr_width)
        self._dmem = DataMem(dmem_addr_width)

        # Synchrone memory write on clock tick
        self._clk.add_trigger(self._imem)
        self._clk.add_trigger(self._dmem)

        # Asynchronous reset register
        self._rst_reg = Register(init_value=0)
        self._clk.add_trigger(self._rst_reg)

        # Processor core instantiation
        self._core = Core(self._clk, rst_reg=self._rst_reg)
    
    @property
    def imem(self) -> InstrMem:
        return self._imem

    @property
    def dmem(self) -> DataMem:
        return self._dmem

    @property
    def reg_file(self) -> RegFile:
        return self._core.rf_inst

    def step(self) -> None:

        # 1. Instruction Fetch Stage
        imem_addr = self._core.get_imem_addr()
        word_imem_addr = imem_addr >> 2
        instr = self._imem.read(word_imem_addr)

        # 2. Decode and evaluate combinational signals (Generates memory addr & write data)
        dmem_data = self._core.dec_exec_alu(instr)

        # 3. Handle Data Memory access based on combinational outputs
        is_dmem_access = True # TEMP HACK, research this
        if is_dmem_access:
            word_dmem_addr = (dmem_data.addr & 0x0FFFFFFF) >> 2

            # Execute memory writes if write enable is active
            if dmem_data.byte_we != 0:
                self._dmem.write(word_dmem_addr, dmem_data.wdata,
                                byte_we=dmem_data.byte_we)

            data_to_cpu = self._dmem.read(word_dmem_addr)
        else:
            data_to_cpu = 0

        # 4. Core Write-Back & Sequential updates (Updates PC and RF)
        self._core.write_back_comb(dmem_data_in=data_to_cpu)

        # 5. Commit all synchronous changes (Clock Tick)
        self._clk.tick()
        
    def get_cur_pc(self):
        return self._core.pc_inst.read()