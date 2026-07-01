from .core.itrigger import ITrigger
from .core.icomb import IComb
from .core.iclock import IClock

class Clock(IClock):
    def __init__(self):
        self._triggers: list[ITrigger] = []
        self._comb: list[IComb] = []

    def add_trigger(self, trigger: ITrigger) -> None:
        if trigger not in self._triggers:
            self._triggers.append(trigger)

    def add_comb(self, comb: IComb):
        if comb not in self._comb:
            self._comb.append(comb)

    def tick(self) -> None:
        for comb in self._comb:
            comb.update()

        for trigger in self._triggers:
            trigger.update()
