from sim_base.clock import Clock
from sim_base.mem.register import Register
from risc_v import riscv_config as conf
from risc_v.modules.mem.dmem import DataMem
from risc_v.modules.mem.imem import InstrMem
from risc_v.riscv_config import *
from .cpu_core import Core


# =========================================================================
# SYSTEM TOP-LEVEL CLASS DEFINITION
# =========================================================================
class CpuSystem:

    def __init__(self,
                 imem_addr_width: int = conf.IMEM_ADDR_BYTE_WIDTH - conf.BYTE_ADDR_WIDTH,
                 dmem_addr_width: int = conf.DMEM_ADDR_BYTE_WIDTH - conf.BYTE_ADDR_WIDTH):
        
        self.clk = Clock()
        
        # Memory instantiation
        self.imem = InstrMem(imem_addr_width)
        self.dmem = DataMem(dmem_addr_width)
        
        # Synchrone memory write on clock tick
        self.clk.add_trigger(self.imem)
        self.clk.add_trigger(self.dmem)
        
        # Asynchronous reset register
        self.rst_reg = Register(init_value=0)
        self.clk.add_trigger(self.rst_reg)
        
        # Processor core instantiation
        self.cpu = Core(self.clk, rst_reg=self.rst_reg)

    def step(self) -> None:
        
        # 1. Instruction Fetch Stage
        imem_addr = self.cpu.get_imem_addr()
        word_imem_addr = imem_addr >> 2
        instr = self.imem.read(word_imem_addr)
        
        # 2. Decode and evaluate combinational signals (Generates memory addr & write data)
        dmem_data = self.cpu.dec_exec_alu(instr)
        
        # 3. Handle Data Memory access based on combinational outputs
        is_dmem_access = (dmem_data.addr >> 28) == 0x0
        if is_dmem_access:
            word_dmem_addr = (dmem_data.addr & 0x0FFFFFFF) >> 2 # FIX ADDR
            
            # Execute memory writes if write enable is active
            if dmem_data.byte_we != 0:
                self.dmem.write(word_dmem_addr, dmem_data.wdata, byte_we=dmem_data.byte_we)
                
            data_to_cpu = self.dmem.read(word_dmem_addr)
        else:
            data_to_cpu = 0
            
        # 4. Core Write-Back & Sequential updates (Updates PC and RF)
        self.cpu.write_back_comb(dmem_data_in=data_to_cpu)
        
        # 5. Commit all synchronous changes (Clock Tick)
        self.clk.tick()