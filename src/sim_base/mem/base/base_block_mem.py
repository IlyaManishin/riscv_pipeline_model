from .memory_array import MemoryArray

class BaseBlockMem(MemoryArray):
    def __init__(self, addr_width: int, cell_size: int, addr_overflow: bool = False):
        size = 1 << addr_width
        super().__init__(size, cell_size)

        self._addr_width: int = addr_width
        self._addr_overflow: bool = addr_overflow
        self._addr_mask: int = (1 << addr_width) - 1

        self._bytes_per_cell: int = cell_size // 8
        self._byte_mask: int = (1 << self._bytes_per_cell) - 1
        self._next_write: tuple[int, int] | None = None

    def get_addr_width(self) -> int:
        return self._addr_width

    def _get_effective_addr(self, addr: int) -> int:
        if self._addr_overflow:
            addr = addr & self._addr_mask
        return addr

    def write(self, addr: int, value: int, byte_we: int | None = None) -> None:
        eff_addr = self._get_effective_addr(addr)

        if self._next_write is not None:
            raise RuntimeError("Memory write conflict: multiple writes detected within a single clock cycle")

        if byte_we == 0:
            return
        if byte_we is None or byte_we == self._byte_mask:
            self._validate_address(eff_addr)
            self._next_write = (eff_addr, value)
            return

        if not (0 <= byte_we <= self._byte_mask):
            raise ValueError(f"Byte write mask {byte_we:#x} out of range")

        merged = self._read_cell(eff_addr)
        for byte_index in range(self._bytes_per_cell):
            if (byte_we >> byte_index) & 1:
                shift = byte_index * 8
                merged = (
                    (merged & ~(0xFF << shift))
                    | (((value >> shift) & 0xFF) << shift)
                )

        self._next_write = (eff_addr, merged)

    def _commit_write(self) -> None:
        if self._next_write is not None:
            addr, val = self._next_write
            self._write_cell(addr, val)
            self._next_write = None