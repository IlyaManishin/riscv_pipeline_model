def disasm(instr: int) -> str:
    instr &= 0xFFFFFFFF

    def bits(hi: int, lo: int) -> int:
        return (instr >> lo) & ((1 << (hi - lo + 1)) - 1)

    def sign_extend(value: int, width: int) -> int:
        if value & (1 << (width - 1)):
            value -= 1 << width
        return value

    # Поля инструкции
    rd = bits(11, 7)
    rs1 = bits(19, 15)
    rs2 = bits(24, 20)
    shamt = rs2

    funct3 = bits(14, 12)
    opcode = bits(6, 2)
    bit30 = bits(30, 30)

    # Ключ как в SV
    case_key = (bit30 << 8) | (funct3 << 5) | opcode

    # ---------- immediates ----------
    imm_i = sign_extend(bits(31, 20), 12)

    imm_s = sign_extend(
        (bits(31, 25) << 5) |
        bits(11, 7),
        12
    )

    imm_b = sign_extend(
        (bits(31, 31) << 12) |
        (bits(7, 7) << 11) |
        (bits(30, 25) << 5) |
        (bits(11, 8) << 1),
        13
    )

    imm_u = bits(31, 12) << 12

    imm_j = sign_extend(
        (bits(31, 31) << 20) |
        (bits(19, 12) << 12) |
        (bits(20, 20) << 11) |
        (bits(30, 21) << 1),
        21
    )
    # -------------------------------

    if opcode == 0b01101:
        return f"lui x{rd}, {imm_u}"

    if opcode == 0b00101:
        return f"auipc x{rd}, {imm_u}"

    if opcode == 0b11011:
        return f"jal x{rd}, {imm_j}"

    if opcode == 0b11001 and funct3 == 0 and bit30 == 0:
        return f"jalr x{rd}, x{rs1}, {imm_i}"

    if opcode == 0b11000:
        if funct3 == 0:
            return f"beq x{rs1}, x{rs2}, {imm_b}"
        if funct3 == 1:
            return f"bne x{rs1}, x{rs2}, {imm_b}"
        if funct3 == 4:
            return f"blt x{rs1}, x{rs2}, {imm_b}"
        if funct3 == 5:
            return f"bge x{rs1}, x{rs2}, {imm_b}"
        if funct3 == 6:
            return f"bltu x{rs1}, x{rs2}, {imm_b}"
        if funct3 == 7:
            return f"bgeu x{rs1}, x{rs2}, {imm_b}"

    if opcode == 0b00000:
        if funct3 == 0:
            return f"lb x{rd}, {imm_i}(x{rs1})"
        if funct3 == 1:
            return f"lh x{rd}, {imm_i}(x{rs1})"
        if funct3 == 2:
            return f"lw x{rd}, {imm_i}(x{rs1})"
        if funct3 == 4:
            return f"lbu x{rd}, {imm_i}(x{rs1})"
        if funct3 == 5:
            return f"lhu x{rd}, {imm_i}(x{rs1})"

    if opcode == 0b01000:
        if funct3 == 0:
            return f"sb x{rs2}, {imm_s}(x{rs1})"
        if funct3 == 1:
            return f"sh x{rs2}, {imm_s}(x{rs1})"
        if funct3 == 2:
            return f"sw x{rs2}, {imm_s}(x{rs1})"

    if opcode == 0b00100:
        if funct3 == 0:
            return f"addi x{rd}, x{rs1}, {imm_i}"
        if funct3 == 2:
            return f"slti x{rd}, x{rs1}, {imm_i}"
        if funct3 == 3:
            return f"sltiu x{rd}, x{rs1}, {imm_i}"
        if funct3 == 4:
            return f"xori x{rd}, x{rs1}, {imm_i}"
        if funct3 == 6:
            return f"ori x{rd}, x{rs1}, {imm_i}"
        if funct3 == 7:
            return f"andi x{rd}, x{rs1}, {imm_i}"
        if funct3 == 1 and bit30 == 0:
            return f"slli x{rd}, x{rs1}, {shamt}"
        if funct3 == 5 and bit30 == 0:
            return f"srli x{rd}, x{rs1}, {shamt}"
        if funct3 == 5 and bit30 == 1:
            return f"srai x{rd}, x{rs1}, {shamt}"

    if opcode == 0b01100:
        if funct3 == 0 and bit30 == 0:
            return f"add x{rd}, x{rs1}, x{rs2}"
        if funct3 == 0 and bit30 == 1:
            return f"sub x{rd}, x{rs1}, x{rs2}"
        if funct3 == 1:
            return f"sll x{rd}, x{rs1}, x{rs2}"
        if funct3 == 2:
            return f"slt x{rd}, x{rs1}, x{rs2}"
        if funct3 == 3:
            return f"sltu x{rd}, x{rs1}, x{rs2}"
        if funct3 == 4:
            return f"xor x{rd}, x{rs1}, x{rs2}"
        if funct3 == 5 and bit30 == 0:
            return f"srl x{rd}, x{rs1}, x{rs2}"
        if funct3 == 5 and bit30 == 1:
            return f"sra x{rd}, x{rs1}, x{rs2}"
        if funct3 == 6:
            return f"or x{rd}, x{rs1}, x{rs2}"
        if funct3 == 7:
            return f"and x{rd}, x{rs1}, x{rs2}"

    # FENCE / FENCE.TSO / PAUSE
    if opcode == 0b00011 and funct3 == 0:
        return "nop"

    # ECALL / EBREAK
    if opcode == 0b11100 and funct3 == 0 and bit30 == 0:
        return "nop"

    return "n/i"