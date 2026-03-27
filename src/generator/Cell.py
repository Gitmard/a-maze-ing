from generator.GeneratorException import GeneratorException
from generator.EDirection import EDirection
from generator.Vec2 import Vec2


class Cell:
    position: Vec2
    locked: bool
    walls: int

    def __init__(
        self,
        position: Vec2,
        walls: int = EDirection.ALL.value,
        locked: bool = False,
    ):
        self.position = position
        self.walls = walls
        self.locked = locked

    def enclose(self, direction: EDirection) -> None:
        if self.locked:
            raise GeneratorException("Cannot edit a locked cell")
        self.walls |= direction.value

    def carve(self, direction: EDirection) -> None:
        if self.locked:
            raise GeneratorException("Cannot edit a locked cell")
        if self.walls & direction.value:
            self.walls -= direction.value

    def reset_cell(self) -> None:
        self.walls = EDirection.ALL.value
        self.locked = False
