from risc_v.riscv_config import XLEN, PC_START_ADDR


class ProgramCounter:

    def __init__(self):
        self.pc = PC_START_ADDR & ((1 << XLEN) - 1)

    def update(
        self,
        rst: bool,
        br_taken: bool,
        pc_br: int
    ) -> int:
        """
        Program Counter.

        Args:
            rst:      Active-high reset.
            br_taken: Branch/jump taken.
            pc_br:    Branch target address.

        Returns:
            Current PC after clock edge.
        """

        mask = (1 << XLEN) - 1

        if rst:
            self.pc = PC_START_ADDR

        elif br_taken:
            self.pc = pc_br & mask

        else:
            self.pc = (self.pc + 4) & mask

        return self.pc

    def get(self) -> int:
        """Current PC value."""
        return self.pc