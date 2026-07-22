from risc_v.riscv_config import *

class Instruction_Decoder:
    
    @staticmethod
    def decode(instr: Instruction, br_eq: bool = False, br_lt: bool = False) -> Id_controls_out:
        opcode = instr.opcode >> 2
        funct3 = instr.funct3
        funct7 = instr.funct7

        # default signals (illegal=1)
        default = Id_controls_out(
            reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
            sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
            alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.ANY,
            imm_type=Instr_type_t.TYPE_ANY, illegal=1, jf_exe=0
        )
        # check first bits of opcode == 11
        if instr.opcode & 0b11 != 0b11:
            return default

        # ---------- LUI ----------
        if opcode == 0b01101:  # 13
            return Id_controls_out(
                reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                alu_sel=Alu_sel_t.LUI, wb_sel=WB_sel_t.ALU_OUT,
                imm_type=Instr_type_t.TYPE_U, illegal=0, jf_exe=0
            )

        # ---------- AUIPC ----------
        if opcode == 0b00101:  # 5
            return Id_controls_out(
                reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel_t.ALU_OUT,
                imm_type=Instr_type_t.TYPE_U, illegal=0, jf_exe=0
            )

        # ---------- JAL ----------
        if opcode == 0b11011:  # 27
            return Id_controls_out(
                reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=0,
                alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel_t.PC4_OUT,
                imm_type=Instr_type_t.TYPE_J, illegal=0, jf_exe=0
            )

        # ---------- JALR ----------
        if opcode == 0b11001 and funct3 == 0b000 and funct7 == 0b0:
            return Id_controls_out(
                reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=0,
                alu_sel=Alu_sel_t.JALR, wb_sel=WB_sel_t.PC4_OUT,
                imm_type=Instr_type_t.TYPE_I, illegal=0, jf_exe=1  # <-- ONLY FOR JALR
            )

        # ---------- Branch instructions ----------
        if opcode == 0b11000:  # 24
            # BEQ
            if funct3 == 0b000:
                if br_eq:
                    return Id_controls_out(
                        reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=0,
                        alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel_t.ANY,
                        imm_type=Instr_type_t.TYPE_B, illegal=0, jf_exe=0
                    )
                else:
                    return Id_controls_out(
                        reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.ANY,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
                    )
            # BNE
            if funct3 == 0b001:
                if not br_eq:
                    return Id_controls_out(
                        reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=0,
                        alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel_t.ANY,
                        imm_type=Instr_type_t.TYPE_B, illegal=0, jf_exe=0
                    )
                else:
                    return Id_controls_out(
                        reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.ANY,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
                    )
            # BLT
            if funct3 == 0b100:
                if br_lt:
                    return Id_controls_out(
                        reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=0,
                        alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel_t.ANY,
                        imm_type=Instr_type_t.TYPE_B, illegal=0, jf_exe=0
                    )
                else:
                    return Id_controls_out(
                        reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.ANY,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
                    )
            # BGE
            if funct3 == 0b101:
                if not br_lt:
                    return Id_controls_out(
                        reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=0,
                        alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel_t.ANY,
                        imm_type=Instr_type_t.TYPE_B, illegal=0, jf_exe=0
                    )
                else:
                    return Id_controls_out(
                        reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.ANY,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
                    )
            # BLTU
            if funct3 == 0b110:
                if br_lt:
                    return Id_controls_out(
                        reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                        sh_sel=Shift_sel_t.ANY, br_un=1, pc_sel=0,
                        alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel_t.ANY,
                        imm_type=Instr_type_t.TYPE_B, illegal=0, jf_exe=0
                    )
                else:
                    return Id_controls_out(
                        reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                        sh_sel=Shift_sel_t.ANY, br_un=1, pc_sel=1,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.ANY,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
                    )
            # BGEU
            if funct3 == 0b111:
                if not br_lt:
                    return Id_controls_out(
                        reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                        sh_sel=Shift_sel_t.ANY, br_un=1, pc_sel=0,
                        alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel_t.ANY,
                        imm_type=Instr_type_t.TYPE_B, illegal=0, jf_exe=0
                    )
                else:
                    return Id_controls_out(
                        reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                        sh_sel=Shift_sel_t.ANY, br_un=1, pc_sel=1,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.ANY,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
                    )
            return default

        # ---------- Load instructions ----------
        if opcode == 0b00000:  # LB, LH, LW, LBU, LHU
            if funct3 in (0b000, 0b001, 0b010, 0b100, 0b101):
                return Id_controls_out(
                    reg_wr=1, dmem_sel=DMem_sel.from_load_funct3(funct3),
                    a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                    alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel_t.DMEM_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0, jf_exe=0
                )
            return default

        # ---------- Store instructions ----------
        if opcode == 0b01000:  # SB, SH, SW
            if funct3 in (0b000, 0b001, 0b010):
                return Id_controls_out(
                    reg_wr=0, dmem_sel=DMem_sel.from_store_funct3(funct3),
                    a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                    alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel_t.ANY,
                    imm_type=Instr_type_t.TYPE_S, illegal=0, jf_exe=0
                )
            return default

        # ---------- Immediate ALU ----------
        if opcode == 0b00100:  # ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI
            if funct3 == 0b000:  # ADDI
                return Id_controls_out(
                    reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                    alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel_t.ALU_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0, jf_exe=0
                )
            if funct3 == 0b010:  # SLTI
                return Id_controls_out(
                    reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                    alu_sel=Alu_sel_t.SLT, wb_sel=WB_sel_t.ALU_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0, jf_exe=0
                )
            if funct3 == 0b011:  # SLTIU
                return Id_controls_out(
                    reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                    alu_sel=Alu_sel_t.SLTU, wb_sel=WB_sel_t.ALU_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0, jf_exe=0
                )
            if funct3 == 0b100:  # XORI
                return Id_controls_out(
                    reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                    alu_sel=Alu_sel_t.XOR, wb_sel=WB_sel_t.ALU_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0, jf_exe=0
                )
            if funct3 == 0b110:  # ORI
                return Id_controls_out(
                    reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                    alu_sel=Alu_sel_t.OR, wb_sel=WB_sel_t.ALU_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0, jf_exe=0
                )
            if funct3 == 0b111:  # ANDI
                return Id_controls_out(
                    reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=0,
                    sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                    alu_sel=Alu_sel_t.AND, wb_sel=WB_sel_t.ALU_OUT,
                    imm_type=Instr_type_t.TYPE_I, illegal=0, jf_exe=0
                )
            if funct3 == 0b001:  # SLLI
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=0,
                        sh_sel=Shift_sel_t.SLL, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.SHIFTER_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0,
                        alushift_sel=1
                    )
            if funct3 == 0b101:  # SRLI / SRAI
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=0,
                        sh_sel=Shift_sel_t.SRL, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.SHIFTER_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0,
                        alushift_sel=1
                    )
                if funct7 == 0b100000:   # 0b1 00000? RISC-V SRAI has funct7[5]=1
                    return Id_controls_out(
                        reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=0,
                        sh_sel=Shift_sel_t.SRA, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.SHIFTER_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0,
                        alushift_sel=1
                    )
            return default

        # ---------- Register ALU ----------
        if opcode == 0b01100:  # ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND
            if funct3 == 0b000:
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.ADD, wb_sel=WB_sel_t.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
                    )
                if funct7 == 0b100000:  # SUB
                    return Id_controls_out(
                        reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.SUB, wb_sel=WB_sel_t.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
                    )
            if funct3 == 0b001:  # SLL
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.SLL, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.SHIFTER_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0,
                        alushift_sel=1
                    )
            if funct3 == 0b010:  # SLT
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.SLT, wb_sel=WB_sel_t.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
                    )
            if funct3 == 0b011:  # SLTU
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.SLTU, wb_sel=WB_sel_t.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
                    )
            if funct3 == 0b100:  # XOR
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.XOR, wb_sel=WB_sel_t.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
                    )
            if funct3 == 0b101:  # SRL / SRA
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.SRL, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.SHIFTER_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0,
                        alushift_sel=1
                    )
                if funct7 == 0b100000:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.SRA, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.SHIFTER_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0,
                        alushift_sel=1
                    )
            if funct3 == 0b110:  # OR
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.OR, wb_sel=WB_sel_t.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
                    )
            if funct3 == 0b111:  # AND
                if funct7 == 0b0:
                    return Id_controls_out(
                        reg_wr=1, dmem_sel = DMem_sel.NONE, a_sel=1, b_sel=1,
                        sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                        alu_sel=Alu_sel_t.AND, wb_sel=WB_sel_t.ALU_OUT,
                        imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
                    )
            return default

        # ---------- FENCE / PAUSE ----------
        if opcode == 0b00011 and funct3 == 0b000:
            return Id_controls_out(
                reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.ANY,
                imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
            )

        # ---------- ECALL / EBREAK ----------
        if opcode == 0b11100 and funct3 == 0b000 and funct7 == 0b0:
            return Id_controls_out(
                reg_wr=0, dmem_sel = DMem_sel.NONE, a_sel=0, b_sel=0,
                sh_sel=Shift_sel_t.ANY, br_un=0, pc_sel=1,
                alu_sel=Alu_sel_t.ANY, wb_sel=WB_sel_t.ANY,
                imm_type=Instr_type_t.TYPE_ANY, illegal=0, jf_exe=0
            )

        # undefined instruction
        return default