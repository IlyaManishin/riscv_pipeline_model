def dmem_rd_port(
    dmem_raw: int,
    byte_addr: int,
    funct3: int
) -> int:
    """
    Data memory read port.

    func3:
        000 - LB
        001 - LH
        010 - LW
        100 - LBU
        101 - LHU
    """
    byte_data = [
        (dmem_raw >> 0) & 0xFF,
        (dmem_raw >> 8) & 0xFF,
        (dmem_raw >> 16) & 0xFF,
        (dmem_raw >> 24) & 0xFF,
    ]

    match funct3:

        # LB
        case 0b000:
            value = byte_data[byte_addr]

            if value & 0x80:
                value |= 0xFFFFFF00

            return value & 0xFFFFFFFF

        # LH
        case 0b001:
            if byte_addr & 0b10:
                value = byte_data[2] | (byte_data[3] << 8)
            else:
                value = byte_data[0] | (byte_data[1] << 8)

            if value & 0x8000:
                value |= 0xFFFF0000

            return value & 0xFFFFFFFF

        # LW
        case 0b010:
            return dmem_raw

        # LBU
        case 0b100:
            return byte_data[byte_addr]

        # LHU
        case 0b101:
            if byte_addr & 0b10:
                return byte_data[2] | (byte_data[3] << 8)
            else:
                return byte_data[0] | (byte_data[1] << 8)

        case _:
            return 0
