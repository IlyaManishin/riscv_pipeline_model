from risc_v.modules.mem.dmem import DataMem


def dmem_wr_port(
    mem: DataMem,
    address: int,
    data: int,
    func3: int,
    we: bool
) -> None:
    """
    Data memory write port.

    func3:
        000 - SB
        001 - SH
        010 - SW
    """

    if not we:
        return

    word_addr = address >> 2
    byte_addr = address & 0b11

    match func3:

        # SB
        case 0b000:
            value = data & 0xFF

            write_data = (
                value |
                (value << 8) |
                (value << 16) |
                (value << 24)
            )

            byte_we = 1 << byte_addr

        # SH
        case 0b001:
            value = data & 0xFFFF

            write_data = value | (value << 16)

            if byte_addr & 0b10:
                byte_we = 0b1100
            else:
                byte_we = 0b0011

        # SW
        case 0b010:
            write_data = data & 0xFFFFFFFF
            byte_we = 0b1111

        case _:
            raise ValueError(f"Unsupported store funct3: {func3:#05b}")

    mem.write(word_addr, write_data, byte_we)