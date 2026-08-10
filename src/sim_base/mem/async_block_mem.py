from .base.base_block_mem import BaseBlockMem


class AsyncBlockMem(BaseBlockMem):
    """
    Asynchronous-read synchronous-write block memory.

    Notes:
        * Reads are asynchronous (combinational).
        * Restricts access to a maximum of 1 read address (multiple reads from the same address are allowed) and 1 write per cycle.
        * Writes are deferred and committed to memory only when `update()` is called.
        * Supports selective sub-word updates via byte-level masking (`byte_we`).
        * Supports address overflow and can get mask from address.
    """

    def __init__(self, addr_width: int, cell_size: int, addr_overflow: bool = False):
        super().__init__(addr_width, cell_size, addr_overflow)
        self._last_read_addr: int | None = None

    def read(self, addr: int) -> int:
        eff_addr = self._get_effective_addr(addr)
        if self._last_read_addr is not None and self._last_read_addr != eff_addr:
            raise RuntimeError(
                "Memory read conflict: multiple reads from different addresses detected within a single clock cycle"
            )
        self._last_read_addr = eff_addr
        return self._read_cell(eff_addr)

    def update(self) -> None:
        self._last_read_addr = None
        self._commit_write()