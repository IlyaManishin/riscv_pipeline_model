from abc import ABC, abstractmethod
from .itrigger import ITrigger

class IRegister(ITrigger, ABC):
    @abstractmethod
    def set(self, next_value: int) -> None:
        pass

    @abstractmethod
    def read(self) -> int:
        pass