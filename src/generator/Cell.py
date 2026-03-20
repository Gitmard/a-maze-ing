from .EDirection import EDirection

from .Vec2 import Vec2


class Cell:
    position: Vec2
    locked: bool
    walls: int

    def __init__(
        self,
        position: Vec2,
        walls: int = 0,
        locked: bool = False
    ):
        self.position = position
        self.walls = walls
        self.locked = locked

    def enclose(
        self,
        direction: EDirection
    ) -> None:
        self.walls |= direction

    def carve(
        self,
        direction: EDirection
    ) -> None:
        if self.walls & direction:
            self.walls -= direction

    def reset_cell(self) -> None:
        self.walls = 0
