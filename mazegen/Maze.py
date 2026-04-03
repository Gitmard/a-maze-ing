"""Grid-based maze data structure with A* solver."""

from mazegen.Cell import Cell
from mazegen.GeneratorException import GeneratorException
from mazegen.Vec2 import Vec2
from mazegen.EDirection import EDirection
from enum import IntEnum, auto
from typing import Dict, List, Literal, Optional, Tuple
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
        """Initialize an empty maze in ``BLANK``
        status with no grid allocated."""
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
        locked_cells: Optional[List[List[Literal[0, 1]]]] = None
    ) -> None:
        """Allocate the grid and optionally overlay the 42 pattern.

        Cells that are part of the 42 pattern are marked as locked,
        preventing the generator from carving through them.

        Args:
            width: Number of columns.
            height: Number of rows.
            start_pos: Maze entry coordinates.
            end_pos: Maze exit coordinates.
            add_ft_pattern: Whether to lock cells forming the 42 logo
                at the center of the grid.

        Raises:
            GeneratorException: If ``start_pos`` or ``end_pos`` falls
                inside the 42 pattern.
        """
        self.status = Maze.Status.INITIALIZED
        self.width = width
        self.height = height
        self.start_pos = start_pos
        self.end_pos = end_pos

        # Init the map as a list of list of cells
        self.map = [
            [Cell(position=Vec2(x, y)) for x in range(width)]
            for y in range(height)
        ]

        if locked_cells is None:
            return

        locked_cells_height = len(locked_cells)
        locked_cells_width = len(locked_cells[0])

        if (
            height >= locked_cells_height + 1
            and width >= locked_cells_width + 1
        ):

            locked_cells_y = int(height / 2 - (locked_cells_height) / 2)
            locked_cells_x = int(width / 2 - (locked_cells_width) / 2)

            for y in range(locked_cells_height):
                for x in range(locked_cells_width):
                    n_x = locked_cells_x + x
                    n_y = locked_cells_y + y
                    self.map[n_y][n_x].locked = locked_cells[y][x] == 1
                    if locked_cells[y][x] == 1 and Vec2(n_x, n_y) in [
                        self.start_pos,
                        self.end_pos,
                    ]:
                        raise GeneratorException(
                            "Entry or exit cannot be in the locked" +
                            " cells pattern"
                        )
        else:
            print(
                "Cannot place the 42 pattern,",
                "will generate the maze without it."
            )

    def carve_cell(self, cell: Cell, directions: int) -> None:
        """Remove walls between a cell and its neighbours
        in the given directions.

        Each direction in the bitmask opens the corresponding wall on ``cell``
        and the matching wall on the adjacent cell (e.g. carving NORTH also
        opens SOUTH on the cell above).

        Args:
            cell: The cell to carve from.
            directions: Bitmask of ``EDirection`` values indicating which
                walls to remove.

        Raises:
            GeneratorException: If ``cell`` is locked, or if carving in a
                direction would go out of bounds.
        """
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

        start_dist = abs(self.end_pos.x - self.start_pos.x) + \
            abs(self.end_pos.y - self.start_pos.y)

        pq: SortedKeyList[Tuple[int, int, Coord], int] = SortedKeyList(
            [(start_dist, 0, start)],
            key=lambda item: -item[0],
        )

        prev: Dict[Coord, Coord] = {}

        best_cost = {start: start_dist}

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

        found: Coord = start

        while pq:
            curr_cost, path, curr = pq.pop()

            if curr_cost > best_cost[curr]:
                continue

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

                dist: int = abs(self.end_pos.x - neighbour[0]) + abs(
                    self.end_pos.y - neighbour[1]
                )

                if neighbour in best_cost:
                    if best_cost[neighbour] <= path + 1 + dist:
                        continue

                best_cost[neighbour] = path + 1 + dist
                prev[neighbour] = curr

                pq.add(
                    (
                        path + 1 + dist,
                        path + 1,
                        neighbour,
                    )
                )

        self.solution = []
        cursor: Coord = found

        while cursor in prev:
            self.solution.append(cursor)
            if cursor == start:
                break
            cursor = prev[cursor]

        self.solution.reverse()
