import enum
import math
from dataclasses import dataclass

XLEN = 32
PC_START_ADDR = 0

IMEM_ADDR_BYTE_WIDTH = 14
DMEM_ADDR_BYTE_WIDTH = 14

DATA_BYTE_NUM = XLEN / 8  # bytes in block with XLEN size
BYTE_ADDR_WIDTH = int(math.log2(DATA_BYTE_NUM))


class Alu_sel_t(enum.Enum):
    ADD = 0b0000
    SUB = 0b0001
    AND = 0b0010
    OR = 0b0011
    XOR = 0b0100
    SLT = 0b0101
    SLTU = 0b0110
    LUI = 0b0111
    JALR = 0b1000
    ANY = 0b1111


class Shift_sel_t(enum.Enum):
    SLL = 0b100
    SRL = 0b010
    SRA = 0b001
    ANY = 0b000


class Instr_type_t(enum.Enum):
    TYPE_I = 0b001
    TYPE_S = 0b010
    TYPE_B = 0b011
    TYPE_U = 0b100
    TYPE_J = 0b101
    TYPE_ANY = 0b000


class WB_sel(enum.Enum):
    PC4_OUT = 0b00
    ALU_OUT = 0b01
    DMEM_OUT = 0b10
    ANY = 0b11


@dataclass
class DMem_sel:
    dmem_we: bool = False
    funct3: int = 0

class Instruction:
    __slots__ = (
        'raw', 'opcode', 'rd', 'funct3', 'rs1', 'rs2',
        'funct7', 'funct7_onebit', 'shamt',
        '_repr_cache', '_str_cache'
    )

    def __init__(self, raw: int = 0x00000013):
        if not (0 <= raw <= 0xFFFFFFFF):
            raise ValueError("Instruction must be 32-bit value")
        self.raw = raw
        
        # Lazy init
        self._repr_cache: str | None = None
        self._str_cache: str | None = None

        self._decode_fields()

    def _decode_fields(self) -> None:
        raw = self.raw
        self.opcode = raw & 0x7F
        self.rd = (raw >> 7) & 0x1F
        self.funct3 = (raw >> 12) & 0x7
        self.rs1 = (raw >> 15) & 0x1F
        self.rs2 = (raw >> 20) & 0x1F
        self.funct7 = (raw >> 25) & 0x7F
        self.funct7_onebit = (raw >> 30) & 0x1
        self.shamt = self.rs2

    def disasm(self) -> str:
        """Return asm representation of instruction."""
        if self._str_cache is not None:
            return self._str_cache

        raw = self.raw

        # Opcode validation (lower 2 bits must be 0b11)
        if (self.opcode & 0x3) != 0x3:
            self._str_cache = "nop"
            return self._str_cache

        op5 = self.opcode >> 2
        rd, rs1, rs2 = self.rd, self.rs1, self.rs2
        f3, bit30 = self.funct3, self.funct7_onebit

        # U-type instructions
        if op5 in (0b01101, 0b00101):
            imm_u = raw & 0xFFFFF000
            if imm_u & 0x80000000:  # Sign extend for 32-bit negative values
                imm_u -= 0x100000000
            mnemonic = "lui" if op5 == 0b01101 else "auipc"
            self._str_cache = f"{mnemonic} x{rd}, {imm_u}"
            return self._str_cache

        # J-type instructions (JAL)
        if op5 == 0b11011:
            imm_j = (
                ((raw >> 11) & 0x100000) |
                (raw & 0xFF000) |
                ((raw >> 20) & 0x800) |
                ((raw >> 20) & 0x7FE)
            )
            if imm_j & 0x100000:
                imm_j -= 0x200000
            self._str_cache = f"jal x{rd}, {imm_j}"
            return self._str_cache

        # I-type immediates calculation
        imm_i = raw >> 20
        if imm_i & 0x800:
            imm_i -= 0x1000

        # I-type jump (JALR)
        if op5 == 0b11001 and f3 == 0 and bit30 == 0:
            self._str_cache = f"jalr x{rd}, x{rs1}, {imm_i}"
            return self._str_cache

        # B-type branch instructions
        if op5 == 0b11000:
            imm_b = ((raw >> 19) & 0x1000) | ((raw << 4) & 0x800) | ((raw >> 20) & 0x7E0) | ((raw >> 7) & 0x1E)
            if imm_b & 0x1000:
                imm_b -= 0x2000
            branches = {0: "beq", 1: "bne", 4: "blt", 5: "bge", 6: "bltu", 7: "bgeu"}
            mnemonic = branches.get(f3)
            if mnemonic:
                self._str_cache = f"{mnemonic} x{rs1}, x{rs2}, {imm_b}"
                return self._str_cache

        # I-type load instructions
        if op5 == 0b00000:
            loads = {0: "lb", 1: "lh", 2: "lw", 4: "lbu", 5: "lhu"}
            mnemonic = loads.get(f3)
            if mnemonic:
                self._str_cache = f"{mnemonic} x{rd}, {imm_i}(x{rs1})"
                return self._str_cache

        # S-type store instructions
        if op5 == 0b01000:
            imm_s = ((raw >> 20) & 0xFE0) | ((raw >> 7) & 0x1F)
            if imm_s & 0x800:
                imm_s -= 0x1000
            stores = {0: "sb", 1: "sh", 2: "sw"}
            mnemonic = stores.get(f3)
            if mnemonic:
                self._str_cache = f"{mnemonic} x{rs2}, {imm_s}(x{rs1})"
                return self._str_cache

        # I-type arithmetic instructions
        if op5 == 0b00100:
            if f3 == 0: self._str_cache = f"addi x{rd}, x{rs1}, {imm_i}"
            elif f3 == 2: self._str_cache = f"slti x{rd}, x{rs1}, {imm_i}"
            elif f3 == 3: self._str_cache = f"sltiu x{rd}, x{rs1}, {imm_i}"
            elif f3 == 4: self._str_cache = f"xori x{rd}, x{rs1}, {imm_i}"
            elif f3 == 6: self._str_cache = f"ori x{rd}, x{rs1}, {imm_i}"
            elif f3 == 7: self._str_cache = f"andi x{rd}, x{rs1}, {imm_i}"
            elif f3 == 1 and bit30 == 0: self._str_cache = f"slli x{rd}, x{rs1}, {self.shamt}"
            elif f3 == 5 and bit30 == 0: self._str_cache = f"srli x{rd}, x{rs1}, {self.shamt}"
            elif f3 == 5 and bit30 == 1: self._str_cache = f"srai x{rd}, x{rs1}, {self.shamt}"
            if self._str_cache is not None:
                return self._str_cache

        # R-type instructions
        if op5 == 0b01100:
            if f3 == 0: mnemonic = "sub" if bit30 else "add"
            elif f3 == 1: mnemonic = "sll"
            elif f3 == 2: mnemonic = "slt"
            elif f3 == 3: mnemonic = "sltu"
            elif f3 == 4: mnemonic = "xor"
            elif f3 == 5: mnemonic = "sra" if bit30 else "srl"
            elif f3 == 6: mnemonic = "or"
            elif f3 == 7: mnemonic = "and"
            else: mnemonic = None

            if mnemonic:
                self._str_cache = f"{mnemonic} x{rd}, x{rs1}, x{rs2}"
                return self._str_cache

        # System & Sync instructions
        if (op5 == 0b00011 and f3 == 0) or (op5 == 0b11100 and f3 == 0 and bit30 == 0):
            self._str_cache = "nop"
            return self._str_cache

        self._str_cache = "n/i"
        return self._str_cache

    def __str__(self) -> str:
        return self.disasm()

    def __repr__(self) -> str:
        if self._repr_cache is None:
            self._repr_cache = (
                f"Instruction("
                f"0x{self.raw:08X}, "
                f"opcode=0x{self.opcode:02X}, "
                f"rd=x{self.rd}, "
                f"rs1=x{self.rs1}, "
                f"rs2=x{self.rs2}, "
                f"funct3=0b{self.funct3:03b}, "
                f"funct7=0b{self.funct7:07b}, "
                f"shamt={self.shamt}"
                f")"
            )
        return self._repr_cache