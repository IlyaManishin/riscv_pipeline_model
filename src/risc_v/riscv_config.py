import enum
import math
from dataclasses import dataclass

XLEN = 32
PC_START_ADDR = 0

IMEM_ADDR_BYTE_WIDTH = 14
DMEM_ADDR_BYTE_WIDTH = 14

DATA_BYTE_NUM   = XLEN / 8 # bytes in block with XLEN size
BYTE_ADDR_WIDTH = int(math.log2(DATA_BYTE_NUM))

class Alu_sel_t(enum.Enum):
    ADD  = 0b0000
    SUB  = 0b0001
    AND  = 0b0010
    OR   = 0b0011
    XOR  = 0b0100
    SLT  = 0b0101
    SLTU = 0b0110
    LUI  = 0b0111
    JALR = 0b1000
    ANY  = 0b0000

class Shift_sel_t(enum.Enum):
    SLL = 0b100
    SRL = 0b010
    SRA = 0b001
    ANY = 0b000

class Instr_type_t(enum.Enum):
    TYPE_I   = 0b001
    TYPE_S   = 0b010
    TYPE_B   = 0b011
    TYPE_U   = 0b100
    TYPE_J   = 0b101
    TYPE_ANY = 0b000

class WB_sel_t(enum.Enum):
    PC4_OUT     = 0b00
    ALU_OUT     = 0b01
    SHIFTER_OUT = 0b10
    DMEM_OUT    = 0b11
    ANY         = 0b00

class DMem_sel(enum.Enum):
    NONE = 0b0000

    LB  = 0b0000
    LH  = 0b0001
    LW  = 0b0010
    LBU = 0b0100
    LHU = 0b0101

    SB  = 0b1000
    SH  = 0b1001
    SW  = 0b1010

    # ---------- Фабричные методы (возвращают DMem_sel) ----------

    @staticmethod
    def from_load_funct3(funct3: int) -> 'DMem_sel':
        match funct3:
            case 0b000: return DMem_sel.LB
            case 0b001: return DMem_sel.LH
            case 0b010: return DMem_sel.LW
            case 0b100: return DMem_sel.LBU
            case 0b101: return DMem_sel.LHU
            case _: raise ValueError(f"Unsupported load funct3: {funct3:#05b}")

    @staticmethod
    def from_store_funct3(funct3: int) -> 'DMem_sel':
        match funct3:
            case 0b000: return DMem_sel.SB
            case 0b001: return DMem_sel.SH
            case 0b010: return DMem_sel.SW
            case _: raise ValueError(f"Unsupported store funct3: {funct3:#05b}")

    @staticmethod
    def from_int(value: int) -> 'DMem_sel':
        """Конвертирует int в DMem_sel, если такое значение существует."""
        for member in DMem_sel:
            if member.value == value:
                return member
        raise ValueError(f"Invalid DMem_sel value: {value:#x}")

    # ---------- Методы экземпляра ----------

    def funct3(self) -> int:
        return self.value & 0b111

    def is_write(self) -> bool:
        return bool(self.value & 0b1000)

    def to_int(self) -> int:
        """Конвертирует DMem_sel в int."""
        return self.value

@dataclass
class Id_controls_out:
    reg_wr: int = 0
    dmem_sel: DMem_sel = DMem_sel.NONE
    a_sel: int = 0
    b_sel: int = 0
    sh_sel: Shift_sel_t   = Shift_sel_t.ANY
    br_un: int = 0
    pc_sel: int = 0
    alu_sel: Alu_sel_t = Alu_sel_t.ANY
    wb_sel: WB_sel_t = WB_sel_t.ANY
    imm_type: int = Instr_type_t.TYPE_ANY
    illegal: int = 0
    jf_exe: int = 0
    alushift_sel: int = 0


class Instruction:
    def __init__(self, raw: int):
        if not (0 <= raw <= 0xFFFFFFFF):
            raise ValueError("Instruction must be 32-bit value")
        self.raw = raw
        self._decode_fields()

    def _decode_fields(self):
        self.opcode = self.raw & 0x7F
        self.rd     = (self.raw >> 7) & 0x1F
        self.funct3  = (self.raw >> 12) & 0x7
        self.rs1    = (self.raw >> 15) & 0x1F
        self.rs2    = (self.raw >> 20) & 0x1F
        self.funct7 = (self.raw >> 25) & 0x7F
        self.funct7_onebit = (self.funct7 >> 5) & 1
        self.shamt = (self.raw >> 20) & 0x1F
    
    def __repr__(self) -> str:
        return (
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

    def __str__(self) -> str:
        """Более компактный вариант для print()."""
        return (
            f"0x{self.raw:08X} | "
            f"op={self.opcode:05b} "
            f"rd=x{self.rd} "
            f"rs1=x{self.rs1} "
            f"rs2=x{self.rs2} "
            f"f3={self.funct3:03b} "
            f"f7={self.funct7:07b}"
        )






