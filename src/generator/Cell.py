from .Vec2 import Vec2


class Cell:
    position: Vec2
    locked: bool
    walls: int
    is_forty_two: bool

    def __init__(
        self,
        position: Vec2,
        locked: bool = False,
        walls: int = 0,
        is_forty_two: bool = False
    ):
        self.position = position
        self.locked = locked or is_forty_two
        self.walls = walls
        self.is_forty_two = is_forty_two

    def carve(
        self,
        directions: int
    ) -> None:
        self.walls |= directions

    def reset_cell(self) -> None:
        self.walls = 0
