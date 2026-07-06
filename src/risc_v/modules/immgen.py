import enum

from risc_v.riscv_config import *

class ImmGen:
    """Генератор непосредственных значений для RISC-V (RV32I)."""
    
    @staticmethod
    def generate(instr: Instruction, imm_type: Instr_type_t) -> int:
        """
        Формирует 32-битное непосредственное значение (imm) на основе инструкции и типа.

        Аргументы:
            instr: объект Instruction (содержит поле raw)
            imm_type: тип непосредственного значения (I, S, B, U, J)

        Возвращает:
            32-битное целое число (знаковое для I/S/B/J, беззнаковое для U)
        """
        raw = instr.raw

        if imm_type == Instr_type_t.TYPE_I:
            # I-type: imm[11:0] = instruction[31:20]
            imm = (raw >> 20) & 0xFFF
            # Знаковое расширение (12 бит)
            if imm & 0x800:
                imm |= 0xFFFFF000
            return imm

        elif imm_type == Instr_type_t.TYPE_S:
            # S-type: imm[11:5] = instruction[31:25], imm[4:0] = instruction[11:7]
            imm = ((raw >> 25) << 5) | ((raw >> 7) & 0x1F)
            # Знаковое расширение (12 бит)
            if imm & 0x800:
                imm |= 0xFFFFF000
            return imm

        elif imm_type == Instr_type_t.TYPE_B:
            # B-type: imm[12] = instruction[31]
            #          imm[11] = instruction[7]
            #          imm[10:5] = instruction[30:25]
            #          imm[4:1] = instruction[11:8]
            #          imm[0] = 0
            imm = ((raw >> 31) << 12) | \
                  (((raw >> 7) & 1) << 11) | \
                  (((raw >> 25) & 0x3F) << 5) | \
                  (((raw >> 8) & 0x0F) << 1)
            # Знаковое расширение (13 бит, бит 12 — знаковый)
            if imm & 0x1000:
                imm |= 0xFFFFE000
            return imm

        elif imm_type == Instr_type_t.TYPE_U:
            # U-type: imm[31:12] = instruction[31:12], младшие 12 бит нули
            imm = (raw >> 12) << 12
            return imm

        elif imm_type == Instr_type_t.TYPE_J:
            # J-type: imm[20] = instruction[31]
            #          imm[19:12] = instruction[19:12]
            #          imm[11] = instruction[20]
            #          imm[10:1] = instruction[30:21]
            #          imm[0] = 0
            imm = ((raw >> 31) << 20) | \
                  (((raw >> 12) & 0xFF) << 12) | \
                  (((raw >> 20) & 1) << 11) | \
                  (((raw >> 21) & 0x3FF) << 1)
            # Знаковое расширение (21 бит, бит 20 — знаковый)
            if imm & 0x100000:
                imm |= 0xFFE00000
            return imm

        else:
            # Неподдерживаемый или ANY тип — возвращаем 0
            return 0