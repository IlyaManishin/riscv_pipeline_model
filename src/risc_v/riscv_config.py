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

@dataclass
class Id_controls_out:
    reg_wr: int = 0
    dmem_sel: DMem_sel = None
    a_sel: int = 0
    b_sel: int = 0
    sh_sel: Shift_sel_t = Shift_sel_t.ANY
    br_un: int = 0
    pc_sel: int = 0
    alu_sel: Alu_sel_t = Alu_sel_t.ANY
    wb_sel: WB_sel = WB_sel.ANY
    imm_type: int = Instr_type_t.TYPE_ANY
    illegal: int = 0
    jfexe: int = 0
    alushift_sel: int = 0

    # workaround for dataclass mutable default error
    def __post_init__(self):
        if self.dmem_sel is None:
            self.dmem_sel = DMem_sel(0, 0)


class Instruction:
    def __init__(self, raw: int):
        if not (0 <= raw <= 0xFFFFFFFF):
            raise ValueError("Instruction must be 32-bit value")
        self.raw = raw
        self._decode_fields()

    def _decode_fields(self):
        self.opcode = self.raw & 0b1111111
        self.rd = (self.raw >> 7) & 0b11111
        self.funct3 = (self.raw >> 12) & 0b111
        self.rs1 = (self.raw >> 15) & 0b11111
        self.rs2 = (self.raw >> 20) & 0b11111
        self.funct7 = (self.raw >> 25) & 0b1111111
        self.funct7_onebit = (self.funct7 >> 5) & 0b1
        self.shamt = (self.raw >> 20) & 0b11111

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
        return (
            f"0x{self.raw:08X} | "
            f"op={self.opcode:05b} "
            f"rd=x{self.rd} "
            f"rs1=x{self.rs1} "
            f"rs2=x{self.rs2} "
            f"f3={self.funct3:03b} "
            f"f7={self.funct7:07b}"
        )
