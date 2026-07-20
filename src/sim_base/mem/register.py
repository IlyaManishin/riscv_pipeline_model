from ..core.itrigger import ITrigger

class Register(ITrigger):
    def __init__(self, init_value: int = 0):
        self._current_value: int = init_value
        self._next_value: int = init_value

    def set(self, next_value: int) -> None:
        self._next_value = next_value
    
    def update(self) -> None:
        self._current_value = self._next_value

    def read(self) -> int:
        return self._current_value

    def set_from_reg(self, reg: Register):
        self.set(reg)