from .base.base_block_mem import BaseBlockMem
from ..core.iregister import IRegister


class BlockMem(BaseBlockMem, IRegister):
    """
    Cell-addressed synchronous block memory.

    Notes:
        * Address width (`addr_width`) is defined in memory cells, not in bits.
        * Operates as a register: set read address on cycle 1, read data on cycle 2.
        * Restricts access to a maximum of 1 write per cycle.
        * Writes and address registrations are deferred and committed only when `update()` is called.
        * Supports selective sub-word updates via byte-level masking (`byte_we`).
        * Supports address overflow and can get mask from address.
    """

    def __init__(self, addr_width: int, cell_size: int, addr_overflow: bool = True):
        super().__init__(addr_width, cell_size, addr_overflow)
        self._current_read_addr: int = None
        self._next_read_addr: int = None

    def set_address(self, addr: int) -> None:
        self._next_read_addr = self._get_effective_addr(addr)

    def set(self, next_value: int) -> None:
        self.set_address(next_value)

    def read(self, addr: int | None = None) -> int:
        if self._current_read_addr is None:
            return 0
        return self._read_cell(self._current_read_addr)

    def update(self) -> None:
        self._current_read_addr = self._next_read_addr
        self._commit_write()