from risc_v.riscv_config import XLEN, Alu_sel_t


class Alu:

    @staticmethod
    def execute(sel: Alu_sel_t, a: int, b: int) -> int:
        """
        Arithmetic Logic Unit.
        """

        mask = (1 << XLEN) - 1

        a &= mask
        b &= mask

        match sel:

            case Alu_sel_t.ADD:
                res = (a + b) & mask

            case Alu_sel_t.SUB:
                res = (a - b) & mask

            case Alu_sel_t.AND:
                res = a & b

            case Alu_sel_t.OR:
                res = a | b

            case Alu_sel_t.XOR:
                res = a ^ b

            case Alu_sel_t.SLT:
                sign_bit = 1 << (XLEN - 1)

                sa = a - (1 << XLEN) if a & sign_bit else a
                sb = b - (1 << XLEN) if b & sign_bit else b

                res = int(sa < sb)

            case Alu_sel_t.SLTU:
                res = int(a < b)

            case Alu_sel_t.JALR:
                res = ((a + b) & mask) & ~1

            case Alu_sel_t.LUI:
                res = b

            case _:
                raise ValueError(f"Unsupported ALU operation: {sel}")

        return res
