from sim_base.mem.register import Register

import risc_v.riscv_config as conf 

class PC:
    def __init__(self, rst_reg: Register, width: int = conf.XLEN, pc_start_addr: int = conf.PC_START_ADDR):
        self._reg = Register(init_value=pc_start_addr)
        
        self.pc_mask = (1 << width) - 1
        self.rst_reg = rst_reg
        self._pc_start_addr = pc_start_addr

    @property
    def reg(self) -> Register:
        return self._reg

    def read(self) -> int:
        return self._reg.read()

    def set_pc(self, br_taken: bool, pc_br: int, pc_stall: bool = False) -> None:
        """always_ff logic"""
        rst = self.rst_reg.read()
        if rst:
            next_pc = self._pc_start_addr
        elif pc_stall:
            next_pc = self._reg.read()
        elif br_taken:
            next_pc = pc_br
        else:
            next_pc = self._reg.read() + 4

        self._reg.set(next_pc & self.pc_mask)
    