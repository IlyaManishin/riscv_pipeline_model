import enum

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


class Id_controls_out:
    def __init__(self, reg_wr=0, dmem_sel=0, a_sel=0, b_sel=0,
                 sh_sel=Shift_sel_t.ANY,
                 br_un=0, pc_sel=0,
                 alu_sel=Alu_sel_t.ANY,
                 wb_sel=WB_sel_t.ANY,
                 imm_type=Instr_type_t.TYPE_ANY,
                 illegal=0, jf_exe=0):
        self.reg_wr   = reg_wr
        self.dmem_sel = dmem_sel
        self.a_sel    = a_sel
        self.b_sel    = b_sel
        self.sh_sel   = sh_sel
        self.br_un    = br_un
        self.pc_sel   = pc_sel
        self.alu_sel  = alu_sel
        self.wb_sel   = wb_sel
        self.imm_type = imm_type
        self.illegal  = illegal
        self.jf_exe   = jf_exe


class Instruction:
    def __init__(self, raw: int):
        if not (0 <= raw <= 0xFFFFFFFF):
            raise ValueError("Instruction must be 32-bit value")
        self.raw = raw
        self._decode_fields()

    def _decode_fields(self):
        self.opcode = self.raw & 0x7F
        self.rd     = (self.raw >> 7) & 0x1F
        self.func3  = (self.raw >> 12) & 0x7
        self.rs1    = (self.raw >> 15) & 0x1F
        self.rs2    = (self.raw >> 20) & 0x1F
        self.funct7 = (self.raw >> 25) & 0x7F
        self.funct7_onebit = (self.funct7 >> 5) & 1
