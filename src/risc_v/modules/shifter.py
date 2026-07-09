from risc_v.riscv_config import XLEN, Shift_sel_t



class Shifter:

    @staticmethod
    def shift(data: int, shamt: int, sel: Shift_sel_t) -> int:
        """
        Shift unit.

        Args:
            data:  XLEN-bit input value.
            shamt: Shift amount.
            sel:   Shift operation.

        Returns:
            Shift result.
        """

        mask = (1 << XLEN) - 1

        data &= mask
        shamt &= (1 << ((XLEN - 1).bit_length())) - 1

        match sel:

            # Logical left
            case Shift_sel_t.SLL:
                res = data << shamt

            # Logical right
            case Shift_sel_t.SRL:
                res = data >> shamt

            # Arithmetic right
            case Shift_sel_t.SRA:
                sign_bit = 1 << (XLEN - 1)

                if data & sign_bit:
                    data -= 1 << XLEN

                res = data >> shamt
            case Shift_sel_t.ANY:
                res = 0

            case _:
                raise ValueError(f"Unsupported shift operation: {sel}")

        return res & mask