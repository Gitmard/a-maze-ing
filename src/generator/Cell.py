from .Vec2 import Vec2
from .EDirection import EDirection

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

    def carve(
        self,
        directions: int
    ) -> None:
        self.walls |= directions

    def reset_cell(self) -> None:
        self.walls = 0
