from risc_v.riscv_config import *


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


# default signals (illegal=1)
DEFAULT_CONTROLS = Id_controls_out(
    reg_wr=0, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
    alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ANY,
    imm_type=Instr_type_t.TYPE_ANY, illegal=1, jfexe=0
)


class InstructionDecoder:
    _DECODE_TABLE: dict[tuple[int, int, int, bool, bool], Id_controls_out] = {}

    @classmethod
    def _build_table(cls) -> None:
        ALL_F7 = range(128)
        ALL_F3 = range(8)

        def register_pattern(op5: int, funct3: int, funct7: int, controls: Id_controls_out) -> None:
            for br_eq in (False, True):
                for br_lt in (False, True):
                    cls._DECODE_TABLE[(op5, funct3, funct7, br_eq, br_lt)] = controls

        # ---------- LUI ----------
        lui_ctrl = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
            alu_sel=Alu_sel_t.LUI, wb_sel=WB_sel.ALU_OUT,
            imm_type=Instr_type_t.TYPE_U, illegal=0, jfexe=0
        )
        for f3 in ALL_F3:
            for f7 in ALL_F7:
                register_pattern(0b01101, f3, f7, lui_ctrl)

        # ---------- AUIPC ----------
        auipc_ctrl = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
            alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.ALU_OUT,
            imm_type=Instr_type_t.TYPE_U, illegal=0, jfexe=0
        )
        for f3 in ALL_F3:
            for f7 in ALL_F7:
                register_pattern(0b00101, f3, f7, auipc_ctrl)

        # ---------- JAL ----------
        jal_ctrl = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=0,
            alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.PC4_OUT,
            imm_type=Instr_type_t.TYPE_J, illegal=0, jfexe=0
        )
        for f3 in ALL_F3:
            for f7 in ALL_F7:
                register_pattern(0b11011, f3, f7, jal_ctrl)

        # ---------- JALR ----------
        jalr_ctrl = Id_controls_out(
            reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=0,
            alu_sel=Alu_sel_t.JALR, wb_sel=WB_sel.PC4_OUT,
            imm_type=Instr_type_t.TYPE_I, illegal=0, jfexe=1  # <-- ONLY FOR JALR
        )
        register_pattern(0b11001, 0b000, 0b0, jalr_ctrl)

        # ---------- Branch instructions ----------
        br_taken = Id_controls_out(
            reg_wr=0, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=0,
            alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.ANY,
            imm_type=Instr_type_t.TYPE_B, illegal=0, jfexe=0
        )
        br_not_taken = Id_controls_out(
            reg_wr=0, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
            alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ANY,
            imm_type=Instr_type_t.TYPE_ANY, illegal=0, jfexe=0
        )
        br_un_taken = Id_controls_out(
            reg_wr=0, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_un=1, pc_sel=0,
            alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.ANY,
            imm_type=Instr_type_t.TYPE_B, illegal=0, jfexe=0
        )
        br_un_not_taken = Id_controls_out(
            reg_wr=0, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_un=1, pc_sel=1,
            alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ANY,
            imm_type=Instr_type_t.TYPE_ANY, illegal=0, jfexe=0
        )

        for f7 in ALL_F7:
            # BEQ
            cls._DECODE_TABLE[(0b11000, 0b000, f7, True, False)] = br_taken
            cls._DECODE_TABLE[(0b11000, 0b000, f7, True, True)] = br_taken
            cls._DECODE_TABLE[(0b11000, 0b000, f7, False, False)] = br_not_taken
            cls._DECODE_TABLE[(0b11000, 0b000, f7, False, True)] = br_not_taken

            # BNE
            cls._DECODE_TABLE[(0b11000, 0b001, f7, False, False)] = br_taken
            cls._DECODE_TABLE[(0b11000, 0b001, f7, False, True)] = br_taken
            cls._DECODE_TABLE[(0b11000, 0b001, f7, True, False)] = br_not_taken
            cls._DECODE_TABLE[(0b11000, 0b001, f7, True, True)] = br_not_taken

            # BLT
            cls._DECODE_TABLE[(0b11000, 0b100, f7, False, True)] = br_taken
            cls._DECODE_TABLE[(0b11000, 0b100, f7, True, True)] = br_taken
            cls._DECODE_TABLE[(0b11000, 0b100, f7, False, False)] = br_not_taken
            cls._DECODE_TABLE[(0b11000, 0b100, f7, True, False)] = br_not_taken

            # BGE
            cls._DECODE_TABLE[(0b11000, 0b101, f7, False, False)] = br_taken
            cls._DECODE_TABLE[(0b11000, 0b101, f7, True, False)] = br_taken
            cls._DECODE_TABLE[(0b11000, 0b101, f7, False, True)] = br_not_taken
            cls._DECODE_TABLE[(0b11000, 0b101, f7, True, True)] = br_not_taken

            # BLTU
            cls._DECODE_TABLE[(0b11000, 0b110, f7, False, True)] = br_un_taken
            cls._DECODE_TABLE[(0b11000, 0b110, f7, True, True)] = br_un_taken
            cls._DECODE_TABLE[(0b11000, 0b110, f7, False, False)] = br_un_not_taken
            cls._DECODE_TABLE[(0b11000, 0b110, f7, True, False)] = br_un_not_taken

            # BGEU
            cls._DECODE_TABLE[(0b11000, 0b111, f7, False, False)] = br_un_taken
            cls._DECODE_TABLE[(0b11000, 0b111, f7, True, False)] = br_un_taken
            cls._DECODE_TABLE[(0b11000, 0b111, f7, False, True)] = br_un_not_taken
            cls._DECODE_TABLE[(0b11000, 0b111, f7, True, True)] = br_un_not_taken

        # ---------- Load instructions ----------
        # LB, LH, LW, LBU, LHU
        for f3 in (0b000, 0b001, 0b010, 0b100, 0b101):
            load_ctrl = Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=f3),
                a_sel=1, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.DMEM_OUT,
                imm_type=Instr_type_t.TYPE_I, illegal=0, jfexe=0
            )
            for f7 in ALL_F7:
                register_pattern(0b00000, f3, f7, load_ctrl)

        # ---------- Store instructions ----------
        # SB, SH, SW
        for f3 in (0b000, 0b001, 0b010):
            store_ctrl = Id_controls_out(
                reg_wr=0, dmem_sel=DMem_sel(dmem_we=1, funct3=f3),
                a_sel=1, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.ANY,
                imm_type=Instr_type_t.TYPE_S, illegal=0, jfexe=0
            )
            for f7 in ALL_F7:
                register_pattern(0b01000, f3, f7, store_ctrl)

        # ---------- Immediate ALU ----------
        # ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI
        imm_alu_ops = {
            0b000: Alu_sel_t.ADD,  # ADDI
            0b010: Alu_sel_t.SLT,  # SLTI
            0b011: Alu_sel_t.SLTU, # SLTIU
            0b100: Alu_sel_t.XOR,  # XORI
            0b110: Alu_sel_t.OR,   # ORI
            0b111: Alu_sel_t.AND,  # ANDI
        }
        for f3, alu_op in imm_alu_ops.items():
            ctrl = Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                alu_sel=alu_op, wb_sel=WB_sel.ALU_OUT,
                imm_type=Instr_type_t.TYPE_I, illegal=0, jfexe=0
            )
            for f7 in ALL_F7:
                register_pattern(0b00100, f3, f7, ctrl)

        # SLLI
        register_pattern(
            0b00100, 0b001, 0b0,
            Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                sh_sel=Shift_sel_t.SLL, br_un=0, pc_sel=1,
                alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
                imm_type=Instr_type_t.TYPE_ANY, illegal=0, jfexe=0,
                alushift_sel=1
            )
        )

        # SRLI / SRAI
        register_pattern(
            0b00100, 0b101, 0b0,
            Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                sh_sel=Shift_sel_t.SRL, br_un=0, pc_sel=1,
                alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
                imm_type=Instr_type_t.TYPE_ANY, illegal=0, jfexe=0,
                alushift_sel=1
            )
        )
        # 0b1 00000? RISC-V SRAI has funct7[5]=1
        register_pattern(
            0b00100, 0b101, 0b0100000,
            Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                sh_sel=Shift_sel_t.SRA, br_un=0, pc_sel=1,
                alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
                imm_type=Instr_type_t.TYPE_ANY, illegal=0, jfexe=0,
                alushift_sel=1
            )
        )

        # ---------- Register ALU ----------
        # ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND
        reg_alu_ops = {
            (0b000, 0b0): Alu_sel_t.ADD,
            (0b000, 0b0100000): Alu_sel_t.SUB,  # SUB
            (0b010, 0b0): Alu_sel_t.SLT,        # SLT
            (0b011, 0b0): Alu_sel_t.SLTU,       # SLTU
            (0b100, 0b0): Alu_sel_t.XOR,        # XOR
            (0b110, 0b0): Alu_sel_t.OR,         # OR
            (0b111, 0b0): Alu_sel_t.AND,        # AND
        }
        for (f3, f7), alu_op in reg_alu_ops.items():
            register_pattern(
                0b01100, f3, f7,
                Id_controls_out(
                    reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                    alu_sel=alu_op, wb_sel=WB_sel.ALU_OUT,
                    imm_type=Instr_type_t.TYPE_ANY, illegal=0, jfexe=0
                )
            )

        # SLL
        register_pattern(
            0b01100, 0b001, 0b0,
            Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                sh_sel=Shift_sel_t.SLL, br_un=0, pc_sel=1,
                alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
                imm_type=Instr_type_t.TYPE_ANY, illegal=0, jfexe=0,
                alushift_sel=1
            )
        )

        # SRL / SRA
        register_pattern(
            0b01100, 0b101, 0b0,
            Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                sh_sel=Shift_sel_t.SRL, br_un=0, pc_sel=1,
                alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
                imm_type=Instr_type_t.TYPE_ANY, illegal=0, jfexe=0,
                alushift_sel=1
            )
        )
        register_pattern(
            0b01100, 0b101, 0b0100000,
            Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                sh_sel=Shift_sel_t.SRA, br_un=0, pc_sel=1,
                alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
                imm_type=Instr_type_t.TYPE_ANY, illegal=0, jfexe=0,
                alushift_sel=1
            )
        )

        # ---------- FENCE / PAUSE ----------
        sys_ctrl = Id_controls_out(
            reg_wr=0, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
            alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ANY,
            imm_type=Instr_type_t.TYPE_ANY, illegal=0, jfexe=0
        )
        for f7 in ALL_F7:
            register_pattern(0b00011, 0b000, f7, sys_ctrl)

        # ---------- ECALL / EBREAK ----------
        register_pattern(0b11100, 0b000, 0b0, sys_ctrl)

    @classmethod
    def decode(cls, instr: Instruction, br_eq: bool = False, br_lt: bool = False) -> Id_controls_out:
        # check first bits of opcode == 11
        if (instr.opcode & 0b11) != 0b11:
            # undefined instruction
            return DEFAULT_CONTROLS

        key = (instr.opcode >> 2, instr.funct3, instr.funct7, bool(br_eq), bool(br_lt))
        return cls._DECODE_TABLE.get(key, DEFAULT_CONTROLS)


InstructionDecoder._build_table()