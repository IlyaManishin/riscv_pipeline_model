from .base_mem import BaseMem


class BlockMem(BaseMem):
    """
    Cell-addressed synchronous block memory.

    Notes:
        * Address width (`addr_width`) is defined in memory cells, not in bits.
        * Strictly restricts access to a maximum of 1 read (many reads from one addr) and 1 write per cycle.
        * Writes are deferred and committed to memory only when `update()` is called.
        * Supports selective sub-word updates via byte-level masking (`byte_we`).
        * Supports address overflow and can get mask from address.
        
    """

    def __init__(self, addr_width: int, cell_size: int, addr_overflow: bool = False):
        size = 1 << addr_width
        super().__init__(size, cell_size)

        self._addr_overflow = addr_overflow
        self._addr_width = addr_width
        self._addr_mask = (1 << addr_width) - 1
        
        self._bytes_per_cell: int = cell_size // 8
        self._byte_mask: int = (1 << self._bytes_per_cell) - 1
        
        self._next_write: tuple[int, int] | None = None
        self._last_read_addr: int = None

    def get_addr_width(self):
        return self._addr_width

    def read(self, addr: int) -> int:
        if (self._addr_overflow):
            addr = addr & self._addr_mask

        if self._last_read_addr is not None and self._last_read_addr != addr:
            raise RuntimeError(
                "Memory read conflict: multiple reads detected within a single clock cycle")
            
        data = self._read_cell(addr)
        self._last_read_addr = addr
        return data

    def write(self, addr: int, value: int, byte_we: int | None = None) -> None:
        if (self._addr_overflow):
            addr = addr & self._addr_mask
            
        if self._next_write is not None:
            raise RuntimeError(
                "Memory write conflict: multiple writes detected within a single clock cycle")

        if byte_we == 0:
            return
        if byte_we is None or byte_we == self._byte_mask:
            self._validate_address(addr)
            self._next_write = (addr, value)
            return

        if not (0 <= byte_we <= self._byte_mask):
            raise ValueError(f"Byte write mask {byte_we:#x} out of range")

        merged = self._read_cell(addr)
        for byte_index in range(self._bytes_per_cell):
            if (byte_we >> byte_index) & 1:
                shift = byte_index * 8
                merged = (
                    (merged & ~(0xFF << shift))
                    | (((value >> shift) & 0xFF) << shift)
                )

        self._next_write = (addr, merged)

    def update(self) -> None:
        self._last_read_addr = None

        if self._next_write is not None:
            addr, val = self._next_write
            self._write_cell(addr, val)
            self._next_write = None
