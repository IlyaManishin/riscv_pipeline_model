from risc_v.modules.mem.dmem import DataMem


def dmem_rd_port(
    mem: DataMem,
    address: int,
    func3: int
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

    word_addr = address >> 2
    byte_addr = address & 0b11

    data = mem.read(word_addr)

    byte_data = [
        (data >> 0) & 0xFF,
        (data >> 8) & 0xFF,
        (data >> 16) & 0xFF,
        (data >> 24) & 0xFF,
    ]

    match func3:

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
            return data

        # LBU
        case 0b100:
            return byte_data[byte_addr]

        # LHU
        case 0b101:
            if byte_addr & 0b10:
                return byte_data[2] | (byte_data[3] << 8)

            return byte_data[0] | (byte_data[1] << 8)

        case _:
            raise ValueError(f"Unsupported load funct3: {func3:#05b}")