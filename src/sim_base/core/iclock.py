from abc import abstractmethod

from .itrigger import ITrigger
from .icomb import IComb

class IClock:

    @abstractmethod
    def add_trigger(self, trigger: ITrigger) -> None:
        pass

    @abstractmethod
    def add_comb(self, comb: IComb):
        pass

    @abstractmethod
    def tick(self) -> None:
        pass