from generator.GeneratorException import GeneratorException
from generator.AsciiMazeVisualizer import AsciiMazeVisualizer
from generator.Maze import Maze
from generator.EDirection import EDirection
from generator.MazeGenerator import MazeGenerator
from generator.Cell import Cell
from generator.Vec2 import Vec2
from typing import List, Optional, Tuple
from sortedcontainers import SortedKeyList
from enum import IntEnum, auto
from copy import copy
from dataclasses import dataclass


class RecursiveDivisionGenerator(MazeGenerator):

    class Direction(IntEnum):
        NONE = auto()
        HORIZONTAL = auto()
        VERTICAL = auto()

    class Position(IntEnum):
        NONE = auto()
        TOP = auto()
        BOTTOM = auto()
        LEFT = auto()
        RIGHT = auto()

    @dataclass
    class DivisionFrame:
        position: "RecursiveDivisionGenerator.Position"
        direction: "RecursiveDivisionGenerator.Direction"
        local_height: int
        local_width: int
        subregion_pos: Vec2
        hardcoded: bool = False

    def __gauss_randint(
        self,
        lower: int,
        upper: int,
        mu: float = 0.5,
        sigma: float = 0.25,
    ) -> int:
        r = max(0, min(1, self._get_rng().gauss(mu, sigma)))
        dist = upper - lower
        return int(lower + (dist * r))

    def __slice_random_vertical(
        self, current_frame: DivisionFrame
    ) -> List[DivisionFrame]:
        # Choose a random coordinate for the slice
        # Pick a new coordinate if the slice
        # we picked intersects with a locked cell
        slice_x = self.__gauss_randint(0, current_frame.local_width - 1)
        return [
            RecursiveDivisionGenerator.DivisionFrame(
                position=RecursiveDivisionGenerator.Position.LEFT,
                direction=RecursiveDivisionGenerator.Direction.VERTICAL,
                local_width=slice_x + 1,
                local_height=current_frame.local_height,
                subregion_pos=copy(current_frame.subregion_pos),
            ),
            RecursiveDivisionGenerator.DivisionFrame(
                position=RecursiveDivisionGenerator.Position.RIGHT,
                direction=RecursiveDivisionGenerator.Direction.VERTICAL,
                local_width=current_frame.local_width - slice_x - 1,
                local_height=current_frame.local_height,
                subregion_pos=Vec2(
                    x=current_frame.subregion_pos.x + slice_x + 1,
                    y=current_frame.subregion_pos.y,
                ),
            ),
        ]

    def __slice_random_horizontal(
        self, current_frame: DivisionFrame
    ) -> List[DivisionFrame]:
        # Choose a random coordinate for the slice
        # Pick a new coordinate if the slice
        # we picked intersects with a locked cell

        slice_y = self.__gauss_randint(0, current_frame.local_height - 1)
        return [
            RecursiveDivisionGenerator.DivisionFrame(
                position=RecursiveDivisionGenerator.Position.TOP,
                direction=RecursiveDivisionGenerator.Direction.HORIZONTAL,
                local_width=current_frame.local_width,
                local_height=slice_y + 1,
                subregion_pos=copy(current_frame.subregion_pos),
            ),
            RecursiveDivisionGenerator.DivisionFrame(
                position=RecursiveDivisionGenerator.Position.BOTTOM,
                direction=RecursiveDivisionGenerator.Direction.HORIZONTAL,
                local_width=current_frame.local_width,
                local_height=current_frame.local_height - slice_y - 1,
                subregion_pos=Vec2(
                    x=current_frame.subregion_pos.x,
                    y=current_frame.subregion_pos.y + slice_y + 1,
                ),
            ),
        ]

    def _carve_around(self, cell: Cell) -> None:
        directions = [
            EDirection.NORTH,
            EDirection.EAST,
            EDirection.SOUTH,
            EDirection.WEST
        ]

        direction_neighbor = {
            EDirection.NORTH: (0, -1),
            EDirection.EAST: (1, 0),
            EDirection.SOUTH: (0, 1),
            EDirection.WEST: (-1, 0),
        }

        opposite_direction = {
            EDirection.NORTH: EDirection.SOUTH,
            EDirection.EAST: EDirection.WEST,
            EDirection.SOUTH: EDirection.NORTH,
            EDirection.WEST: EDirection.EAST
        }

        for dir in directions:
            is_open = not bool(cell.walls & dir.value)
            x, y = cell.position.x, cell.position.y
            move_x, move_y = direction_neighbor[dir]
            n_x, n_y = x + move_x, y + move_y

            if n_x not in range(self.get_maze().width):
                continue
            if n_y not in range(self.get_maze().height):
                continue
            if self.get_maze().map[n_y][n_x].locked:
                continue

            n_cell = self.get_maze().map[n_y][n_x]

            opposite = opposite_direction[dir]

            if is_open:
                n_cell.walls &= ~opposite.value
            else:
                n_cell.walls |= opposite.value

    def __slice_random(
        self,
        current_frame: DivisionFrame,
        direction: "RecursiveDivisionGenerator.Direction",
    ) -> List[DivisionFrame]:
        if direction == RecursiveDivisionGenerator.Direction.VERTICAL:
            return self.__slice_random_vertical(current_frame)
        else:
            return self.__slice_random_horizontal(current_frame)

    def __create_new_frames(
        self, current_frame: DivisionFrame
    ) -> List[DivisionFrame]:
        # Choose the direction of the slice
        # If the current slice is taller than it is wide,
        # Slice horizontally
        if current_frame.local_height > current_frame.local_width:
            return self.__slice_random(
                current_frame, RecursiveDivisionGenerator.Direction.HORIZONTAL
            )

        # The current slice is wider than it is tall,
        # Slice vertically
        if current_frame.local_height < current_frame.local_width:
            return self.__slice_random(
                current_frame, RecursiveDivisionGenerator.Direction.VERTICAL
            )

        # The current slice is as wide as it is tall
        # Pick a random direction
        return self.__slice_random(
            current_frame,
            (
                RecursiveDivisionGenerator.Direction.VERTICAL
                if self._get_rng().randint(0, 1) == 1
                else RecursiveDivisionGenerator.Direction.HORIZONTAL
            ),
        )

    def __add_vertical_wall(self, current_frame: DivisionFrame) -> List[Cell]:
        edited_cells: List[Cell] = []

        # The wall's x coordinate is constantP
        wall_x = current_frame.subregion_pos.x + current_frame.local_width - 1

        if wall_x + 1 >= self.get_maze().width:
            return []

        # Loop through the wall's height
        for y in range(
            current_frame.subregion_pos.y,
            current_frame.subregion_pos.y + current_frame.local_height,
        ):
            curr_cells = [
                self.get_maze().map[y][wall_x],
                self.get_maze().map[y][wall_x + 1],
            ]

            # Update the cells adjacent to the wall
            if not curr_cells[0].locked:
                curr_cells[0].enclose(EDirection.EAST)
            if not curr_cells[1].locked:
                curr_cells[1].enclose(EDirection.WEST)
            edited_cells.extend(curr_cells)

        # Choose a random coordinate for the opening
        # We bound the coordinate from the beginning to the height - 2
        # For a slice of width 10, the opening will be between y=0 and y=8
        # Pick a new coordinate if we chose a locked cell
        opening_y = -1
        available_y_pos = list(
            range(
                current_frame.subregion_pos.y,
                current_frame.subregion_pos.y + current_frame.local_height,
            )
        )
        while (
            opening_y == -1
            or self.get_maze().map[opening_y][wall_x].locked
            or self.get_maze().map[opening_y][wall_x + 1].locked
        ):
            if not len(available_y_pos):
                raise (
                    GeneratorException(
                        "No available space to add openning"
                    )
                )
            opening_y = available_y_pos.pop(
                self.__gauss_randint(0, len(available_y_pos) - 1)
            )

        # Carve the cells with the opening
        self.get_maze().map[opening_y][wall_x].carve(EDirection.EAST)
        self.get_maze().map[opening_y][wall_x + 1].carve(EDirection.WEST)
        return edited_cells

    def __add_horizontal_wall(
        self, current_frame: DivisionFrame
    ) -> List[Cell]:
        edited_cells: List[Cell] = []

        # The wall's Y coordinate is constant
        wall_y = current_frame.subregion_pos.y + current_frame.local_height - 1

        if wall_y + 1 >= self.get_maze().height:
            return []

        # Loop through the wall's width
        for x in range(
            current_frame.subregion_pos.x,
            current_frame.subregion_pos.x + current_frame.local_width,
        ):
            curr_cells = [
                self.get_maze().map[wall_y][x],
                self.get_maze().map[wall_y + 1][x],
            ]

            # Update the cells adjacent to the wall
            if not curr_cells[0].locked:
                curr_cells[0].enclose(EDirection.SOUTH)
            if not curr_cells[0].locked:
                curr_cells[1].enclose(EDirection.NORTH)
            edited_cells.extend(curr_cells)

        # Choose a random coordinate for the opening
        # We bound the coordinate from the beginning to the width - 2
        # For a slice of width 10, the opening will be between x=0 and x=8
        # Loop until we pick a non-locked cell
        opening_x = -1
        available_x_pos = list(
            range(
                current_frame.subregion_pos.x,
                current_frame.subregion_pos.x + current_frame.local_width - 1,
            )
        )
        while (
            opening_x == -1
            or self.get_maze().map[wall_y][opening_x].locked
            or self.get_maze().map[wall_y + 1][opening_x].locked
        ):
            if not len(available_x_pos):
                raise (
                    GeneratorException(
                        "No available space to add openning"
                    )
                )
            opening_x = available_x_pos.pop(
                self.__gauss_randint(0, len(available_x_pos) - 1)
            )
        # Carve the cells with the opening
        self.get_maze().map[wall_y][opening_x].carve(EDirection.SOUTH)
        self.get_maze().map[wall_y + 1][opening_x].carve(EDirection.NORTH)
        return edited_cells

    def __add_wall(self, current_frame: DivisionFrame) -> List[Cell]:
        if (
            current_frame.direction
            == RecursiveDivisionGenerator.Direction.VERTICAL
        ):
            return self.__add_vertical_wall(current_frame)
        else:
            return self.__add_horizontal_wall(current_frame)

    def _would_create_open_3x3(
        self,
        cell_x: int,
        cell_y: int,
        direction: EDirection,
    ) -> bool:
        """Check if removing a wall would complete a 3x3 open zone.

        Args:
            cell_x: X coordinate of the cell losing a wall.
            cell_y: Y coordinate of that cell.
            direction: The wall being removed.

        Returns:
            ``True`` if the removal would complete a fully open
            3x3 block, ``False`` if it is safe.
        """
        maze = self.get_maze()
        grid = maze.map

        if direction == EDirection.EAST:
            edge_cols = (cell_x, cell_x + 1)
            edge_row = cell_y
            is_vertical = True
        elif direction == EDirection.WEST:
            edge_cols = (cell_x - 1, cell_x)
            edge_row = cell_y
            is_vertical = True
        elif direction == EDirection.SOUTH:
            edge_rows = (cell_y, cell_y + 1)
            edge_col = cell_x
            is_vertical = False
        else:  # NORTH
            edge_rows = (cell_y - 1, cell_y)
            edge_col = cell_x
            is_vertical = False

        candidates: List[Tuple[int, int]] = []
        if is_vertical:
            for cx in range(edge_cols[0] - 1, edge_cols[0] + 1):
                for cy in range(edge_row - 2, edge_row + 1):
                    candidates.append((cx, cy))
        else:
            for cy in range(edge_rows[0] - 1, edge_rows[0] + 1):
                for cx in range(edge_col - 2, edge_col + 1):
                    candidates.append((cx, cy))

        for cx, cy in candidates:
            if (
                cx < 0 or cx + 2 >= maze.width
                or cy < 0 or cy + 2 >= maze.height
            ):
                continue

            all_open = True

            for r in range(cy, cy + 3):
                for c in range(cx, cx + 2):
                    is_target = (
                        c == cell_x
                        and r == cell_y
                        and direction == EDirection.EAST
                    ) or (
                        c + 1 == cell_x
                        and r == cell_y
                        and direction == EDirection.WEST
                    )
                    if not is_target and (
                        grid[r][c].walls & EDirection.EAST.value
                    ):
                        all_open = False
                        break
                if not all_open:
                    break

            if not all_open:
                continue

            for r in range(cy, cy + 2):
                for c in range(cx, cx + 3):
                    is_target = (
                        c == cell_x
                        and r == cell_y
                        and direction == EDirection.SOUTH
                    ) or (
                        c == cell_x
                        and r + 1 == cell_y
                        and direction == EDirection.NORTH
                    )
                    if not is_target and (
                        grid[r][c].walls & EDirection.SOUTH.value
                    ):
                        all_open = False
                        break
                if not all_open:
                    break

            if all_open:
                return True

        return False

    def _make_imperfect(self) -> None:
        directions = [
            EDirection.NORTH,
            EDirection.EAST,
            EDirection.SOUTH,
            EDirection.WEST
        ]

        direction_neighbor = {
            EDirection.NORTH: (0, -1),
            EDirection.EAST: (1, 0),
            EDirection.SOUTH: (0, 1),
            EDirection.WEST: (-1, 0),
        }

        maze = self.get_maze()

        def count_walls(cell: Cell):
            c = 0
            for dir in directions:
                if cell.walls & dir.value:
                    c += 1
            return c

        temp_available_cells: List[Cell] = [
            cell
            for row in maze.map
            for cell in row
            if not cell.locked
        ]

        self._get_rng().shuffle(temp_available_cells)

        available_cells: SortedKeyList[Cell] = SortedKeyList(
            temp_available_cells,
            key=lambda x: count_walls(x)
        )

        wall_number = sum([
            1 for cell in available_cells
            for dir in directions
            if cell.walls & dir.value
        ])

        wall_number -= (maze.height + maze.width) * 2

        wall_number //= 2

        walls_to_break = int(wall_number * 0.3)
        walls_to_break = max(1, walls_to_break)

        print(walls_to_break)

        break_count = 0
        while break_count < walls_to_break and available_cells:
            cell = available_cells.pop()
            x, y = cell.position.x, cell.position.y
            self._get_rng().shuffle(directions)

            for dir in directions:
                breaked = False

                if not (cell.walls & dir.value):
                    continue

                move_x, move_y = direction_neighbor[dir]
                n_x, n_y = x + move_x, y + move_y

                if n_x not in range(maze.width):
                    continue
                if n_y not in range(maze.height):
                    continue
                if maze.map[n_y][n_x].locked:
                    continue

                if self._would_create_open_3x3(x, y, dir):
                    continue

                cell.walls &= ~dir.value
                self._carve_around(cell)
                break_count += 1
                breaked = True
                break

            if breaked:
                available_cells.add(cell)

        print(break_count)

    def generate(
        self, seed: Optional[str] = None, show_progress: bool = False
    ) -> List[Cell]:

        if seed is not None:
            self._get_rng().seed(seed)

        if self.get_maze().status == Maze.Status.GENERATED:
            self.reset_maze()

        # Initialize the stack with a frame of the full maze
        stack: List[RecursiveDivisionGenerator.DivisionFrame] = (
            [
                RecursiveDivisionGenerator.DivisionFrame(
                    position=(RecursiveDivisionGenerator.Position.LEFT),
                    direction=(RecursiveDivisionGenerator.Direction.VERTICAL),
                    local_height=self.get_maze().height,
                    local_width=self.get_maze().ft_pattern_start.x,
                    subregion_pos=Vec2(0, 0),
                    hardcoded=True,
                ),
                RecursiveDivisionGenerator.DivisionFrame(
                    position=(RecursiveDivisionGenerator.Position.LEFT),
                    direction=(RecursiveDivisionGenerator.Direction.VERTICAL),
                    local_height=self.get_maze().ft_pattern_start.y,
                    local_width=(
                        self.get_maze().ft_pattern_end.x
                        - self.get_maze().ft_pattern_start.x
                    ),
                    subregion_pos=Vec2(self.get_maze().ft_pattern_start.x, 0),
                    hardcoded=True,
                ),
                RecursiveDivisionGenerator.DivisionFrame(
                    position=(RecursiveDivisionGenerator.Position.LEFT),
                    direction=(RecursiveDivisionGenerator.Direction.VERTICAL),
                    local_height=(
                        self.get_maze().height
                        - self.get_maze().ft_pattern_end.y
                    ),
                    local_width=(
                        self.get_maze().ft_pattern_end.x
                        - self.get_maze().ft_pattern_start.x
                    ),
                    subregion_pos=Vec2(
                        self.get_maze().ft_pattern_start.x,
                        self.get_maze().ft_pattern_end.y,
                    ),
                    hardcoded=True,
                ),
                RecursiveDivisionGenerator.DivisionFrame(
                    position=(RecursiveDivisionGenerator.Position.RIGHT),
                    direction=(RecursiveDivisionGenerator.Direction.VERTICAL),
                    local_height=self.get_maze().height,
                    local_width=(
                        self.get_maze().width
                        - self.get_maze().ft_pattern_end.x
                    ),
                    subregion_pos=Vec2(self.get_maze().ft_pattern_end.x, 0),
                    hardcoded=True,
                ),
                RecursiveDivisionGenerator.DivisionFrame(
                    position=RecursiveDivisionGenerator.Position.TOP,
                    direction=RecursiveDivisionGenerator.Direction.HORIZONTAL,
                    local_width=2,
                    local_height=2,
                    subregion_pos=Vec2(
                        self.get_maze().ft_pattern_start.x,
                        self.get_maze().ft_pattern_end.y - 2,
                    ),
                    hardcoded=True,
                ),
            ]
            if len(self.get_maze().locked_cells)
            else [
                RecursiveDivisionGenerator.DivisionFrame(
                    position=RecursiveDivisionGenerator.Position.NONE,
                    direction=RecursiveDivisionGenerator.Direction.NONE,
                    local_height=self.get_maze().height,
                    local_width=self.get_maze().width,
                    subregion_pos=Vec2(0, 0),
                )
            ]
        )

        updated_cells: List[Cell] = []
        while len(stack):
            # Get the frame to process
            current_frame = stack.pop()

            if current_frame.hardcoded and (
                current_frame.position
                == RecursiveDivisionGenerator.Position.LEFT
                or current_frame.position
                == RecursiveDivisionGenerator.Position.TOP
            ):
                if show_progress:
                    AsciiMazeVisualizer.display_maze(self.get_maze())
                    command = input("Press enter to continue, q to quit... ")
                    if command == "q":
                        return updated_cells
                self.__add_wall(current_frame)

            # Stop condition, the frame will be skipped if too small
            if min(current_frame.local_height, current_frame.local_width) <= 1:
                continue

            new_frames = []

            try:
                # Slice the current frame in two
                new_frames = self.__create_new_frames(current_frame)
                # print("New frames:", new_frames, sep="\n")

                # Add a wall using the first frame
                # For a vertical split, the index 0
                # will always be the top frame
                # For horizontal, the left frame
                # Since the frames share the same wall,
                # we can call add_wall only once
                # We only use the "first" frame here, so for a vertical split,
                # The X coordinate of the wall will be
                # the local width of the frame
                # For horizontal, Y is the local height
                if show_progress:
                    AsciiMazeVisualizer.display_maze(self.get_maze())
                    command = input("Press enter to continue, q to quit... ")
                    if command == "q":
                        return updated_cells
                updated_cells.extend(self.__add_wall(new_frames[0]))
            except GeneratorException as err:
                print(err)

            # Add the new frames to the stack
            stack.extend(new_frames)
        self.get_maze().status = Maze.Status.GENERATED
        self._make_imperfect()
        return updated_cells
