from .base_mem import BaseMem

class BlockMem(BaseMem):
    def __init__(self, addr_width: int, cell_size: int):
        size = 1 << addr_width
        super().__init__(size, cell_size)
        
        self._bytes_per_cell: int = cell_size // 8
        self._byte_mask: int = (1 << self._bytes_per_cell) - 1
        self._next_write: tuple[int, int] | None = None
        self._has_read_this_cycle: bool = False
    
    def read(self, address: int) -> int:
        self._validate_address(address)
        if self._has_read_this_cycle:
            raise RuntimeError("Memory read conflict: multiple reads detected within a single clock cycle")
        
        self._has_read_this_cycle = True
        return self._memory[address]

    def write_cell(self, address: int, value: int) -> None:
        self._validate_address(address)
        if self._next_write is not None:
            raise RuntimeError("Memory write conflict: multiple writes detected within a single clock cycle")
        self._next_write = (address, value & self._mask)

    def write(self, address: int, value: int, byte_we: int | None = None) -> None:
        self._validate_address(address)

        if self._next_write is not None:
            raise RuntimeError("Memory write conflict: multiple writes detected within a single clock cycle")

        if byte_we is None:
            self.write_cell(address, value)
            return

        if not (0 <= byte_we <= self._byte_mask):
            raise ValueError(f"Byte write mask {byte_we:#x} out of range")

        if byte_we == 0:
            return

        if byte_we == self._byte_mask:
            self.write_cell(address, value)
            return

        merged = self._memory[address]
        for byte_index in range(self._bytes_per_cell):
            if (byte_we >> byte_index) & 1:
                shift = byte_index * 8
                merged = (
                    (merged & ~(0xFF << shift))
                    | (((value >> shift) & 0xFF) << shift)
                )

        self.write_cell(address, merged)

    def update(self) -> None:
        self._has_read_this_cycle = False
        
        if self._next_write is not None:
            addr, val = self._next_write
            self._memory[addr] = val
            self._next_write = None