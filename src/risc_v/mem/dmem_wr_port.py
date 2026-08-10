def dmem_wr_port(data: int, byte_offset: int, funct3: int) -> tuple[int, int]:
    """
    Data memory write port.

    func3:
        000 - SB
        001 - SH
        010 - SW
    """
    match funct3:

        # SB
        case 0b000:
            value = data & 0xFF

            write_data = (
                value |
                (value << 8) |
                (value << 16) |
                (value << 24)
            )

            byte_we = 1 << byte_offset
            return write_data, byte_we

        # SH
        case 0b001:
            value = data & 0xFFFF

            write_data = value | (value << 16)

            if byte_offset & 0b10:
                byte_we = 0b1100
            else:
                byte_we = 0b0011
                
            return write_data, byte_we

        # SW
        case 0b010:
            write_data = data & 0xFFFFFFFF
            byte_we = 0b1111
            return write_data, byte_we

        case _:
            raise ValueError(f"Unsupported store funct3: {funct3:#05b}")