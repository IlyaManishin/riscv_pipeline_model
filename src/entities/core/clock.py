from ..core.itrigger import ITrigger

class Clock:
    def __init__(self):
        self._triggers: list[ITrigger] = []

    def register(self, trigger: ITrigger) -> None:
        if trigger not in self._triggers:
            self._triggers.append(trigger)

    def tick(self) -> None:
        for trigger in self._triggers:
            trigger.update()