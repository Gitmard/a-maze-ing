from .Cell import Cell
from .Vec2 import Vec2
from typing import List


class Maze:
    map: List[List[Cell]]
    width: int
    height: int

    def __init__(self) -> None:
        self.map = []
        self.height = 0
        self.width = 0

    def reset_map(self) -> None:
        for line in self.map:
            for cell in line:
                cell.reset_cell()

    def init_map(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.map = [
            [Cell(position=Vec2(x, y)) for x in range(width)]
            for y in range(height)
        ]
