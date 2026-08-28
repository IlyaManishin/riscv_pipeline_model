from risc_v.riscv_config import *


@dataclass
class Id_controls_out:
    reg_wr: int = 0
    dmem_sel: DMem_sel = None
    a_sel: int = 0
    b_sel: int = 0
    sh_sel: Shift_sel_t = Shift_sel_t.ANY
    br_un: int = 0
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


class InstructionDecoder:

    @staticmethod
    def decode(instr: Instruction) -> Id_controls_out:
        opcode = instr.opcode >> 2
        funct3 = instr.funct3
        funct7 = instr.funct7

        # default signals (illegal=1)
        default = Id_controls_out(
            reg_wr=0, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
            alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ANY,
            imm_type=Instr_type_t.TYPE_ANY, illegal=1
        )
        # check first bits of opcode == 11
        if instr.opcode & 0b11 != 0b11:
            return default

        # ---------- LUI ----------
        if opcode == 0b01101:  # 13
            return Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                alu_sel=Alu_sel_t.LUI, wb_sel=WB_sel.ALU_OUT,
                imm_type=Instr_type_t.TYPE_U, illegal=0
            )

        # ---------- AUIPC ----------
        if opcode == 0b00101:  # 5
            return Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.ALU_OUT,
                imm_type=Instr_type_t.TYPE_U, illegal=0
            )

        # ---------- JAL ----------
        if opcode == 0b11011:  # 27
            return Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=0, br_unit_sel=0,
                alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.PC4_OUT,
                imm_type=Instr_type_t.TYPE_J, illegal=0
            )

        # ---------- JALR ----------
        if opcode == 0b11001 and funct3 == 0b000 and funct7 == 0b0:
            return Id_controls_out(
                reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=0, br_unit_sel=0,
                alu_sel=Alu_sel_t.JALR, wb_sel=WB_sel.PC4_OUT,
                imm_type=Instr_type_t.TYPE_I, illegal=0
            )

        # ---------- Branch instructions ----------
        if opcode == 0b11000:  # 24
            if funct3 in (0b000, 0b001, 0b100, 0b101, 0b110, 0b111):
                br_un = 1 if funct3 in (0b110, 0b111) else 0
                return Id_controls_out(
                    reg_wr=0, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=br_un, pc_sel=0, br_unit_sel=1,
                    alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.ANY,
                    imm_type=Instr_type_t.TYPE_B, illegal=0
                )
            return default

        # ---------- Load instructions ----------
        if opcode == 0b00000:  # LB, LH, LW, LBU, LHU
            if funct3 in (0b000, 0b001, 0b010, 0b100, 0b101):
                return Id_controls_out(
                    reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=funct3),
                    a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                    alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.DMEM_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0
                )
            return default

        # ---------- Store instructions ----------
        if opcode == 0b01000:  # SB, SH, SW
            if funct3 in (0b000, 0b001, 0b010):
                return Id_controls_out(
                    reg_wr=0, dmem_sel=DMem_sel(dmem_we=1, funct3=funct3),
                    a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                    alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.ANY,
                    imm_type=Instr_type_t.TYPE_S, illegal=0
                )
            return default

        # ---------- Immediate ALU ----------
        if opcode == 0b00100:  # ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI
            if funct3 == 0b000:  # ADDI
                return Id_controls_out(
                    reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                    alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.ALU_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0
                )
            if funct3 == 0b010:  # SLTI
                return Id_controls_out(
                    reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                    alu_sel=Alu_sel_t.SLT, wb_sel=WB_sel.ALU_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0
                )
            if funct3 == 0b011:  # SLTIU
                return Id_controls_out(
                    reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                    alu_sel=Alu_sel_t.SLTU, wb_sel=WB_sel.ALU_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0
                )
            if funct3 == 0b100:  # XORI
                return Id_controls_out(
                    reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                    alu_sel=Alu_sel_t.XOR, wb_sel=WB_sel.ALU_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0
                )
            if funct3 == 0b110:  # ORI
                return Id_controls_out(
                    reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                    alu_sel=Alu_sel_t.OR, wb_sel=WB_sel.ALU_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0
                )
            if funct3 == 0b111:  # ANDI
                return Id_controls_out(
                    reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                    alu_sel=Alu_sel_t.AND, wb_sel=WB_sel.ALU_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0
                )
            if funct3 == 0b001:  # SLLI
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                        sh_sel=Shift_sel_t.SLL, br_un=0, pc_sel=1, br_unit_sel=0,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0,
                        alushift_sel=1
                    )
            if funct3 == 0b101:  # SRLI / SRAI
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                        sh_sel=Shift_sel_t.SRL, br_un=0, pc_sel=1, br_unit_sel=0,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0,
                        alushift_sel=1
                    )
                if funct7 == 0b100000:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=0,
                        sh_sel=Shift_sel_t.SRA, br_un=0, pc_sel=1, br_unit_sel=0,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0,
                        alushift_sel=1
                    )
            return default

        # ---------- Register ALU ----------
        if opcode == 0b01100:  # ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND
            if funct3 == 0b000:
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                        alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0
                    )
                if funct7 == 0b100000:  # SUB
                    return Id_controls_out(
                        reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                        alu_sel=Alu_sel_t.SUB, wb_sel=WB_sel.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0
                    )
            if funct3 == 0b001:  # SLL
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.SLL, br_un=0, pc_sel=1, br_unit_sel=0,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0,
                        alushift_sel=1
                    )
            if funct3 == 0b010:  # SLT
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                        alu_sel=Alu_sel_t.SLT, wb_sel=WB_sel.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0
                    )
            if funct3 == 0b011:  # SLTU
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                        alu_sel=Alu_sel_t.SLTU, wb_sel=WB_sel.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0
                    )
            if funct3 == 0b100:  # XOR
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                        alu_sel=Alu_sel_t.XOR, wb_sel=WB_sel.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0
                    )
            if funct3 == 0b101:  # SRL / SRA
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.SRL, br_un=0, pc_sel=1, br_unit_sel=0,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0,
                        alushift_sel=1
                    )
                if funct7 == 0b100000:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.SRA, br_un=0, pc_sel=1, br_unit_sel=0,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0,
                        alushift_sel=1
                    )
            if funct3 == 0b110:  # OR
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                        alu_sel=Alu_sel_t.OR, wb_sel=WB_sel.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0
                    )
            if funct3 == 0b111:  # AND
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                        alu_sel=Alu_sel_t.AND, wb_sel=WB_sel.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0
                    )
            return default

        # ---------- FENCE / PAUSE ----------
        if opcode == 0b00011 and funct3 == 0b000:
            return Id_controls_out(
                reg_wr=0, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ANY,
                imm_type=Instr_type_t.TYPE_ANY, illegal=0
            )

        # ---------- ECALL / EBREAK ----------
        if opcode == 0b11100 and funct3 == 0b000 and funct7 == 0b0:
            return Id_controls_out(
                reg_wr=0, dmem_sel=DMem_sel(dmem_we=0, funct3=0), a_sel=0, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1, br_unit_sel=0,
                alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel.ANY,
                imm_type=Instr_type_t.TYPE_ANY, illegal=0
            )

        # undefined instruction
        return default