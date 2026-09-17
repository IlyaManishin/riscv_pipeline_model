from risc_v.riscv_config import *


@dataclass
class Id_controls_out:
    reg_wr: int = 0
    dmem_sel: DMem_sel = None
    a_sel: int = 0
    b_sel: int = 0
    sh_sel: Shift_sel_t = Shift_sel_t.ANY
    br_unsigned: int = 0
    pc_sel: int = 1
    br_unit_sel: int = 0
    alu_sel: Alu_sel_t = Alu_sel_t.ANY
    wb_sel: WB_sel = WB_sel.ANY
    imm_type: int = Instr_type_t.TYPE_ANY
    illegal: int = 0
    alushift_sel: int = 0

    # workaround for dataclass mutable default error
    def __post_init__(self):
        if self.dmem_sel is None:
            self.dmem_sel = DMem_sel(0, 0)


# default signals (illegal=1)
DEFAULT_CONTROLS = Id_controls_out(
    reg_wr=0, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
    sh_sel=Shift_sel_t.ANY, br_unsigned=0, pc_sel=1, br_unit_sel=0,
    alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ANY,
    imm_type=Instr_type_t.TYPE_ANY, illegal=1
)


class InstructionDecoder:
    _DECODE_TABLE: dict[tuple[int, int, int], Id_controls_out] = {}

    @classmethod
    def _build_table(cls):
        ALL_F7 = range(128)
        ALL_F3 = range(8)

        # ---------- LUI ----------
        lui_ctrl = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_unsigned=0, pc_sel=1, br_unit_sel=0,
            alu_sel=Alu_sel_t.LUI, wb_sel=WB_sel.ALU_OUT,
            imm_type=Instr_type_t.TYPE_U, illegal=0
        )
        for f3 in ALL_F3:
            for f7 in ALL_F7:
                cls._DECODE_TABLE[(0b01101, f3, f7)] = lui_ctrl

        # ---------- AUIPC ----------
        auipc_ctrl = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_unsigned=0, pc_sel=1, br_unit_sel=0,
            alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.ALU_OUT,
            imm_type=Instr_type_t.TYPE_U, illegal=0
        )
        for f3 in ALL_F3:
            for f7 in ALL_F7:
                cls._DECODE_TABLE[(0b00101, f3, f7)] = auipc_ctrl

        # ---------- JAL ----------
        jal_ctrl = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_unsigned=0, pc_sel=0, br_unit_sel=0,
            alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.PC4_OUT,
            imm_type=Instr_type_t.TYPE_J, illegal=0
        )
        for f3 in ALL_F3:
            for f7 in ALL_F7:
                cls._DECODE_TABLE[(0b11011, f3, f7)] = jal_ctrl

        # ---------- JALR ----------
        cls._DECODE_TABLE[(0b11001, 0b000, 0b0)] = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_unsigned=0, pc_sel=0, br_unit_sel=0,
            alu_sel=Alu_sel_t.JALR, wb_sel=WB_sel.PC4_OUT,
            imm_type=Instr_type_t.TYPE_I, illegal=0
        )

        # ---------- Branch instructions ----------
        for f3 in (0b000, 0b001, 0b100, 0b101, 0b110, 0b111):
            br_un = 1 if f3 in (0b110, 0b111) else 0
            br_ctrl = Id_controls_out(
                reg_wr=0, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_unsigned=br_un, pc_sel=0, br_unit_sel=1,
                alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.ANY,
                imm_type=Instr_type_t.TYPE_B, illegal=0
            )
            for f7 in ALL_F7:
                cls._DECODE_TABLE[(0b11000, f3, f7)] = br_ctrl

        # ---------- Load instructions ----------
        for f3 in (0b000, 0b001, 0b010, 0b100, 0b101):
            load_ctrl = Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=f3),
                a_sel=1, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_unsigned=0, pc_sel=1, br_unit_sel=0,
                alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.DMEM_OUT,
                imm_type=Instr_type_t.TYPE_I, illegal=0
            )
            for f7 in ALL_F7:
                cls._DECODE_TABLE[(0b00000, f3, f7)] = load_ctrl

        # ---------- Store instructions ----------
        for f3 in (0b000, 0b001, 0b010):
            store_ctrl = Id_controls_out(
                reg_wr=0, dmem_sel=DMem_sel(dmem_we=1, funct3=f3),
                a_sel=1, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_unsigned=0, pc_sel=1, br_unit_sel=0,
                alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.ANY,
                imm_type=Instr_type_t.TYPE_S, illegal=0
            )
            for f7 in ALL_F7:
                cls._DECODE_TABLE[(0b01000, f3, f7)] = store_ctrl

        # ---------- Immediate ALU ----------
        imm_alu_ops = {
            0b000: Alu_sel_t.ADD,
            0b010: Alu_sel_t.SLT,
            0b011: Alu_sel_t.SLTU,
            0b100: Alu_sel_t.XOR,
            0b110: Alu_sel_t.OR,
            0b111: Alu_sel_t.AND,
        }
        for f3, alu_op in imm_alu_ops.items():
            ctrl = Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_unsigned=0, pc_sel=1, br_unit_sel=0,
                alu_sel=alu_op, wb_sel=WB_sel.ALU_OUT,
                imm_type=Instr_type_t.TYPE_I, illegal=0
            )
            for f7 in ALL_F7:
                cls._DECODE_TABLE[(0b00100, f3, f7)] = ctrl

        cls._DECODE_TABLE[(0b00100, 0b001, 0b0)] = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
            sh_sel=Shift_sel_t.SLL, br_unsigned=0, pc_sel=1, br_unit_sel=0,
            alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
            imm_type=Instr_type_t.TYPE_ANY, illegal=0,
            alushift_sel=1
        )
        cls._DECODE_TABLE[(0b00100, 0b101, 0b0)] = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
            sh_sel=Shift_sel_t.SRL, br_unsigned=0, pc_sel=1, br_unit_sel=0,
            alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
            imm_type=Instr_type_t.TYPE_ANY, illegal=0,
            alushift_sel=1
        )
        cls._DECODE_TABLE[(0b00100, 0b101, 0b0100000)] = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
            sh_sel=Shift_sel_t.SRA, br_unsigned=0, pc_sel=1, br_unit_sel=0,
            alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
            imm_type=Instr_type_t.TYPE_ANY, illegal=0,
            alushift_sel=1
        )

        # ---------- Register ALU ----------
        reg_alu_ops = {
            (0b000, 0b0): Alu_sel_t.ADD,
            (0b000, 0b0100000): Alu_sel_t.SUB,
            (0b010, 0b0): Alu_sel_t.SLT,
            (0b011, 0b0): Alu_sel_t.SLTU,
            (0b100, 0b0): Alu_sel_t.XOR,
            (0b110, 0b0): Alu_sel_t.OR,
            (0b111, 0b0): Alu_sel_t.AND,
        }
        for (f3, f7), alu_op in reg_alu_ops.items():
            cls._DECODE_TABLE[(0b01100, f3, f7)] = Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                sh_sel=Shift_sel_t.ANY, br_unsigned=0, pc_sel=1, br_unit_sel=0,
                alu_sel=alu_op, wb_sel=WB_sel.ALU_OUT,
                imm_type=Instr_type_t.TYPE_ANY, illegal=0
            )

        cls._DECODE_TABLE[(0b01100, 0b001, 0b0)] = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
            sh_sel=Shift_sel_t.SLL, br_unsigned=0, pc_sel=1, br_unit_sel=0,
            alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
            imm_type=Instr_type_t.TYPE_ANY, illegal=0,
            alushift_sel=1
        )
        cls._DECODE_TABLE[(0b01100, 0b101, 0b0)] = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
            sh_sel=Shift_sel_t.SRL, br_unsigned=0, pc_sel=1, br_unit_sel=0,
            alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
            imm_type=Instr_type_t.TYPE_ANY, illegal=0,
            alushift_sel=1
        )
        cls._DECODE_TABLE[(0b01100, 0b101, 0b0100000)] = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
            sh_sel=Shift_sel_t.SRA, br_unsigned=0, pc_sel=1, br_unit_sel=0,
            alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
            imm_type=Instr_type_t.TYPE_ANY, illegal=0,
            alushift_sel=1
        )

        # ---------- FENCE / PAUSE ----------
        sys_ctrl = Id_controls_out(
            reg_wr=0, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_unsigned=0, pc_sel=1, br_unit_sel=0,
            alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ANY,
            imm_type=Instr_type_t.TYPE_ANY, illegal=0
        )
        for f7 in ALL_F7:
            cls._DECODE_TABLE[(0b00011, 0b000, f7)] = sys_ctrl

        # ---------- ECALL / EBREAK ----------
        cls._DECODE_TABLE[(0b11100, 0b000, 0b0)] = sys_ctrl

    @classmethod
    def decode(cls, instr: Instruction) -> Id_controls_out:
        # check first bits of opcode == 11
        if (instr.opcode & 0b11) != 0b11:
            return DEFAULT_CONTROLS

        key = (instr.opcode >> 2, instr.funct3, instr.funct7)
        return cls._DECODE_TABLE.get(key, DEFAULT_CONTROLS)


InstructionDecoder._build_table()