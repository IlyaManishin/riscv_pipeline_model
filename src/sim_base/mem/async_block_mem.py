from .base.base_block_mem import BaseBlockMem


class AsyncBlockMem(BaseBlockMem):
    """
    Asynchronous-read synchronous-write block memory.

    Notes:
        * Reads are asynchronous (combinational) with no single-cycle access restrictions.
        * Allow many reads and only 1 write per cycle.
        * Writes are deferred and committed to memory only when `update()` is called.
        * Supports selective sub-word updates via byte-level masking (`byte_we`).
        * Supports address overflow and can get mask from address.
    """

    def read(self, address: int) -> int:
        eff_addr = self._get_effective_addr(address)
        return self._read_cell(eff_addr)

    def update(self) -> None:
        self._commit_write()