"""Grid-based maze data structure with A* solver."""

from enum import IntEnum, auto
from typing import Dict, List, Set, Tuple

from sortedcontainers import SortedKeyList

from generator.EDirection import EDirection

from .Cell import Cell
from .Vec2 import Vec2

Coord = Tuple[int, int]


class Maze:
    """Two-dimensional grid maze with generation and solving support.

    Attributes:
        map: 2-D grid of ``Cell`` objects (row-major).
        width: Number of columns.
        height: Number of rows.
        status: Current lifecycle stage of the maze.
        start_pos: Entry cell coordinates.
        end_pos: Exit cell coordinates.
        solution: Ordered list of ``(x, y)`` pairs from entry
            to exit, populated after :meth:`solve` is called.
    """

    class Status(IntEnum):
        """Maze lifecycle stages."""

        BLANK = auto()
        INITIALIZED = auto()
        GENERATED = auto()
        SOLVED = auto()

    map: List[List[Cell]]
    width: int
    height: int
    status: "Maze.Status"
    start_pos: Vec2
    end_pos: Vec2

    def __init__(self) -> None:
        self.map: List[List[Cell]] = []
        self.height = 0
        self.width = 0
        self.status = Maze.Status.BLANK
        self.solution: List[Coord] = []

    def reset_map(self) -> None:
        """Reset every cell and revert status to ``BLANK``."""
        self.status = Maze.Status.BLANK
        for line in self.map:
            for cell in line:
                cell.reset_cell()

    def init_map(
        self,
        width: int,
        height: int,
        start_pos: Vec2,
        end_pos: Vec2,
    ) -> None:
        """Allocate the grid and seal the border walls.

        Args:
            width: Number of columns.
            height: Number of rows.
            start_pos: Maze entry coordinates.
            end_pos: Maze exit coordinates.
        """
        self.status = Maze.Status.INITIALIZED
        self.width = width
        self.height = height
        self.start_pos = start_pos
        self.end_pos = end_pos

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

    def solve(self) -> None:
        """Find the shortest path from entry to exit using A*.

        Results are stored in :attr:`solution` as a list of
        ``(x, y)`` coordinate tuples ordered from start to end.
        """
        start: Coord = (self.start_pos.x, self.start_pos.y)
        end: Coord = (self.end_pos.x, self.end_pos.y)

        pq: SortedKeyList[Tuple[int, int, Coord]] = SortedKeyList(
            [(0, 0, start)],
            key=lambda item: -item[0],
        )

        prev: Dict[Coord, Coord] = {}
        directions: List[EDirection] = [
            EDirection.NORTH,
            EDirection.EAST,
            EDirection.SOUTH,
            EDirection.WEST,
        ]

        moves: Dict[EDirection, Coord] = {
            EDirection.NORTH: (0, -1),
            EDirection.EAST: (1, 0),
            EDirection.SOUTH: (0, 1),
            EDirection.WEST: (-1, 0),
        }

        explored: Set[Coord] = {start}
        found: Coord = start

        while pq:
            _, path, curr = pq.pop(0)
            x, y = curr
            curr_cell: Cell = self.map[y][x]

            if curr == end:
                found = curr
                break

            for direction in directions:
                if curr_cell.walls & direction.value:
                    continue

                move_x, move_y = moves[direction]
                neighbour: Coord = (x + move_x, y + move_y)

                if neighbour in explored:
                    continue

                explored.add(neighbour)

                dist: int = (
                    abs(self.end_pos.x - neighbour[0])
                    + abs(self.end_pos.y - neighbour[1])
                )

                pq.add((
                    -path - 1 - dist,
                    path + 1,
                    neighbour,
                ))

                if neighbour not in prev:
                    prev[neighbour] = curr

        self.solution = []
        cursor: Coord = found

        while cursor in prev:
            self.solution.append(cursor)
            if cursor == start:
                break
            cursor = prev[cursor]

        self.solution.reverse()
