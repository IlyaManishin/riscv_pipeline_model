from abc import ABC, abstractmethod

from sim_base.mem.block_mem import BlockMem
from risc_v.mem.reg_file import RegFile


class ICpuSystem(ABC):
    @property
    @abstractmethod
    def imem(self) -> BlockMem:
        pass

    @property
    @abstractmethod
    def dmem(self) -> BlockMem:
        pass

    @property
    @abstractmethod
    def reg_file(self) -> RegFile:
        pass

    @abstractmethod
    def step(self) -> None:
        pass
    
    @abstractmethod
    def get_cur_pc(self) -> int:
        pass
