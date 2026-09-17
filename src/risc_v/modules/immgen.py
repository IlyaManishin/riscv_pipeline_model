from risc_v.riscv_config import *
from typing import Callable

class ImmGen:
    """Immediate value generator for RISC-V (RV32I)."""

    @staticmethod
    def _gen_i(raw: int) -> int:
        imm = (raw >> 20) & 0xFFF
        return (imm | 0xFFFFF000) if (imm & 0x800) else imm

    @staticmethod
    def _gen_s(raw: int) -> int:
        imm = ((raw >> 25) << 5) | ((raw >> 7) & 0x1F)
        return (imm | 0xFFFFF000) if (imm & 0x800) else imm

    @staticmethod
    def _gen_b(raw: int) -> int:
        imm = (((raw >> 31) & 1) << 12) | \
              (((raw >> 7) & 1) << 11) | \
              (((raw >> 25) & 0x3F) << 5) | \
              (((raw >> 8) & 0x0F) << 1)
        return (imm | 0xFFFFE000) if (imm & 0x1000) else imm

    @staticmethod
    def _gen_u(raw: int) -> int:
        return raw & 0xFFFFF000

    @staticmethod
    def _gen_j(raw: int) -> int:
        imm = (((raw >> 31) & 1) << 20) | \
              (((raw >> 12) & 0xFF) << 12) | \
              (((raw >> 20) & 1) << 11) | \
              (((raw >> 21) & 0x3FF) << 1)
        return (imm | 0xFFE00000) if (imm & 0x100000) else imm

    _DECODERS: dict = None

    @staticmethod
    def generate(instr: Instruction, imm_type: Instr_type_t) -> int:
        """
        Build a 32-bit immediate value (imm) from the instruction and type.

        Arguments:
            instr: Instruction object containing the raw instruction field.
            imm_type: Immediate value type (I, S, B, U, or J).

        Returns:
            A 32-bit integer (signed for I/S/B/J and unsigned for U).
        """
        if ImmGen._DECODERS is None:
            ImmGen._DECODERS = {
                Instr_type_t.TYPE_I: ImmGen._gen_i,
                Instr_type_t.TYPE_S: ImmGen._gen_s,
                Instr_type_t.TYPE_B: ImmGen._gen_b,
                Instr_type_t.TYPE_U: ImmGen._gen_u,
                Instr_type_t.TYPE_J: ImmGen._gen_j,
            }
            
        decoder = ImmGen._DECODERS.get(imm_type)
        if decoder is not None:
            return decoder(instr.raw)
        return 0


