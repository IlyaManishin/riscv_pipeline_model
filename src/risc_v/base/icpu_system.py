from abc import ABC, abstractmethod

from risc_v.modules.mem.imem import InstrMem
from risc_v.modules.mem.dmem import DataMem
from risc_v.modules.mem.reg_file import RegFile


class ICpuSystem(ABC):
    @property
    @abstractmethod
    def imem(self) -> InstrMem:
        pass

    @property
    @abstractmethod
    def dmem(self) -> DataMem:
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
