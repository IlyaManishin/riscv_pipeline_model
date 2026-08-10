from sim_base.mem.register import Register

import risc_v.riscv_config as conf


class PC:
    def __init__(self, rst_reg: Register, width: int = conf.XLEN, pc_start_addr: int = conf.PC_START_ADDR):
        self._reg: Register[int] = Register(init_value=pc_start_addr)

        self.pc_mask = (1 << width) - 1
        self.rst_reg = rst_reg
        self._pc_start_addr = pc_start_addr

    @property
    def reg(self) -> Register:
        return self._reg

    def read(self) -> int:
        return self._reg.read()

    def get_pc_next(self, br_taken: bool, pc_br: int) -> int:
        rst = self.rst_reg.read()
        if rst:
            next_pc_raw = self._pc_start_addr
        elif br_taken:
            next_pc_raw = pc_br
        else:
            next_pc_raw = self._reg.read()

        next_pc = next_pc_raw & self.pc_mask
        return next_pc

    def update_pc(self, br_taken: bool, pc_br: int) -> None:
        """always_ff logic. Only for syngle-cycle"""
        rst = self.rst_reg.read()
        if rst:
            next_pc_raw = self._pc_start_addr
        elif br_taken:
            next_pc_raw = pc_br
        else:
            next_pc_raw = self._reg.read() + 4

        next_pc = next_pc_raw & self.pc_mask
        self._reg.set(next_pc)

    def set_pc(self, pc_next):
        self._reg.set(pc_next & self.pc_mask)

    def stall(self):
        self._reg.set(self._reg.read())
