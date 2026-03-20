from .Cell import Cell
from .Vec2 import Vec2
from typing import List


class Maze:
    map: List[List[Cell]]

    def __init__(self) -> None:
        self.map = []

    def reset_map(self) -> None:
        for line in self.map:
            for cell in line:
                cell.reset_cell()

    def init_map(self, width: int, height: int) -> None:
        self.map = [
            [Cell(position=Vec2(x, y)) for x in range(width)]
            for y in range(height)
        ]
        # TODO: Add 42 cells in the middle :3
