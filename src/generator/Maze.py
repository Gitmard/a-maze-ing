"""Grid-based maze data structure with A* solver."""

from generator.Cell import Cell
from generator.GeneratorException import GeneratorException
from generator.Vec2 import Vec2
from generator.EDirection import EDirection
from enum import IntEnum, auto
from typing import Dict, List, Literal, Set, Tuple
from sortedcontainers import SortedKeyList

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
        GENERATING = auto()
        GENERATED = auto()
        SOLVED = auto()

    map: List[List[Cell]]
    width: int
    height: int
    status: "Maze.Status"
    start_pos: Vec2
    end_pos: Vec2
    locked_cells: List[Cell]
    add_ft_pattern: bool
    solution: List[Coord]

    def __init__(self) -> None:
        self.map: List[List[Cell]] = []
        self.height = 0
        self.width = 0
        self.status = Maze.Status.BLANK
        self.start_pos = Vec2(0, 0)
        self.end_pos = Vec2(0, 0)
        self.locked_cells = []
        self.ft_pattern_end = Vec2(0, 0)
        self.add_ft_pattern = False
        self.solution = []

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
        add_ft_pattern: bool = False,
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
        self.add_ft_pattern = add_ft_pattern

        # Init the map as a list of list of cells
        self.map = [
            [Cell(position=Vec2(x, y)) for x in range(width)]
            for y in range(height)
        ]

        # Put the ft pattern at the center of the maze
        ft_pattern: List[List[Literal[0, 1]]] = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1],
        ]
        ft_pattern_height = len(ft_pattern)
        ft_pattern_width = len(ft_pattern[0])

        if (
            add_ft_pattern
            and height >= ft_pattern_height + 1
            and width >= ft_pattern_width + 1
        ):

            ft_pattern_y = int(height / 2 - (ft_pattern_height) / 2)
            ft_pattern_x = int(width / 2 - (ft_pattern_width) / 2)

            for y in range(ft_pattern_height):
                for x in range(ft_pattern_width):
                    n_x = ft_pattern_x + x
                    n_y = ft_pattern_y + y
                    self.map[n_y][n_x].locked = (
                        ft_pattern[y][x] == 1
                    )
                    if ft_pattern[y][x] == 1 and \
                            Vec2(n_x, n_y) in [self.start_pos, self.end_pos]:
                        raise GeneratorException(
                            "Entry or exit cannot be in the 42 pattern"
                        )

    def carve_cell(self, cell: Cell, directions: int) -> None:
        if cell.locked:
            raise GeneratorException("Cannot carve a locked cell")

        if directions & EDirection.NORTH.value:
            if cell.position.y <= 0:
                raise GeneratorException(
                    "Cannot carve a cell with y = 0 to the north"
                )
            self.map[cell.position.y - 1][cell.position.x].carve(
                EDirection.SOUTH
            )
            cell.carve(EDirection.NORTH)

        if directions & EDirection.EAST.value:
            if cell.position.x >= self.width - 1:
                raise GeneratorException(
                    "Cannot carve a cell with x = width - 1 to the east"
                )
            self.map[cell.position.y][cell.position.x + 1].carve(
                EDirection.WEST
            )
            cell.carve(EDirection.EAST)

        if directions & EDirection.SOUTH.value:
            if cell.position.y >= self.height - 1:
                raise GeneratorException(
                    "Cannot carve a cell with y = height - 1 to the south"
                )
            self.map[cell.position.y + 1][cell.position.x].carve(
                EDirection.NORTH
            )
            cell.carve(EDirection.SOUTH)

        if directions & EDirection.WEST.value:
            if cell.position.x <= 0:
                raise GeneratorException(
                    "Cannot carve a cell with x = 0 to the west"
                )
            self.map[cell.position.y][cell.position.x - 1].carve(
                EDirection.EAST
            )
            cell.carve(EDirection.WEST)

    def solve(self) -> None:
        """Find the shortest path from entry to exit using A*.

        Results are stored in :attr:`solution` as a list of
        ``(x, y)`` coordinate tuples ordered from start to end.
        """
        start: Coord = (self.start_pos.x, self.start_pos.y)
        end: Coord = (self.end_pos.x, self.end_pos.y)

        pq: SortedKeyList[Tuple[int, int, Coord], int] = SortedKeyList(
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

                dist: int = abs(self.end_pos.x - neighbour[0]) + abs(
                    self.end_pos.y - neighbour[1]
                )

                pq.add(
                    (
                        -path - 1 - dist,
                        path + 1,
                        neighbour,
                    )
                )

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
