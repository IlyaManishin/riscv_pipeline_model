from risc_v.riscv_config import XLEN


class BranchUnit:

    @staticmethod
    def compare(rd1: int, rd2: int, br_un: bool) -> tuple[bool, bool]:
        """
        Compare two XLEN-bit values.

        Args:
            rd1: First operand.
            rd2: Second operand.
            br_un: False - signed compare, True - unsigned compare.

        Returns:
            (br_eq, br_lt)
        """

        mask = (1 << XLEN) - 1

        rd1 &= mask
        rd2 &= mask

        br_eq = (rd1 == rd2)

        if br_un:
            br_lt = rd1 < rd2
        else:
            sign_bit = 1 << (XLEN - 1)

            if rd1 & sign_bit:
                rd1 -= 1 << XLEN

            if rd2 & sign_bit:
                rd2 -= 1 << XLEN

            br_lt = rd1 < rd2

        return br_eq, br_lt