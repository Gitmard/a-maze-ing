from generator.EDirection import EDirection

from .Cell import Cell
from .Vec2 import Vec2
from enum import IntEnum, auto
from typing import List


class Maze:

    class Status(IntEnum):
        BLANK = auto()
        INITIALIZED = auto()
        GENERATED = auto()
        SOLVED = auto()

    map: List[List[Cell]]
    width: int
    height: int
    status: "Maze.Status"

    def __init__(self) -> None:
        self.map = []
        self.height = 0
        self.width = 0
        self.status = Maze.Status.BLANK

    def reset_map(self) -> None:
        self.status = Maze.Status.BLANK
        for line in self.map:
            for cell in line:
                cell.reset_cell()

    def init_map(self, width: int, height: int) -> None:
        self.status = Maze.Status.INITIALIZED
        self.width = width
        self.height = height
        self.map = [
            [Cell(position=Vec2(x, y)) for x in range(width)]
            for y in range(height)
        ]
        for x in range(width):
            self.map[0][x].enclose(EDirection.NORTH)
            self.map[height - 1][x].enclose(EDirection.SOUTH)
        for y in range(height):
            self.map[y][0].enclose(EDirection.WEST)
            self.map[y][width - 1].enclose(EDirection.EAST)
