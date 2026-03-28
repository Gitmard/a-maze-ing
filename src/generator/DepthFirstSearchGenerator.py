from generator.Maze import Maze
from generator.EDirection import EDirection
from generator.MazeGenerator import MazeGenerator
from generator.Cell import Cell
from typing import List, Optional, Set, Tuple
from sortedcontainers import SortedKeyList


class DepthFirstSearchGenerator(MazeGenerator):

    def get_random_direction(
        self, curr_cell: Cell, visited_cells: Set[Cell]
    ) -> Optional[EDirection]:
        avaiable_directions: List[EDirection] = []

        if (
            curr_cell.position.y > 0
            and not self.get_maze()
            .map[curr_cell.position.y - 1][curr_cell.position.x]
            .locked
            and self.get_maze().map[curr_cell.position.y - 1][
                curr_cell.position.x
            ] not in visited_cells
        ):
            avaiable_directions.append(EDirection.NORTH)

        if (
            curr_cell.position.x > 0
            and not self.get_maze()
            .map[curr_cell.position.y][curr_cell.position.x - 1]
            .locked
            and self.get_maze().map[curr_cell.position.y][
                curr_cell.position.x - 1
            ] not in visited_cells
        ):
            avaiable_directions.append(EDirection.WEST)

        if (
            curr_cell.position.y < self.get_maze().height - 1
            and not self.get_maze()
            .map[curr_cell.position.y + 1][curr_cell.position.x]
            .locked
            and self.get_maze().map[curr_cell.position.y + 1][
                curr_cell.position.x
            ] not in visited_cells
        ):
            avaiable_directions.append(EDirection.SOUTH)

        if (
            curr_cell.position.x < self.get_maze().width - 1
            and not self.get_maze()
            .map[curr_cell.position.y][curr_cell.position.x + 1]
            .locked
            and self.get_maze().map[curr_cell.position.y][
                curr_cell.position.x + 1
            ] not in visited_cells
        ):
            avaiable_directions.append(EDirection.EAST)

        if not len(avaiable_directions):
            return None

        return avaiable_directions[
            self._get_rng().randint(0, len(avaiable_directions) - 1)
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

        walls_to_break = int(wall_number * 0.2)
        walls_to_break = max(1, walls_to_break)

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

    def generate(
        self, seed: Optional[str] = None
    ) -> List[Cell]:

        if seed is not None:
            self._get_rng().seed(seed)

        if self.get_maze().status == Maze.Status.GENERATED:
            self.reset_maze()

        self.get_maze().status = Maze.Status.GENERATING

        updated_cells: List[Cell] = [self.get_maze().map[0][0]]

        stack: List[Cell] = [self.get_maze().map[0][0]]
        visited_cells: Set[Cell] = set()

        stack_len = 1

        while stack_len:
            curr_cell = stack[stack_len - 1]
            visited_cells.add(curr_cell)
            direction = self.get_random_direction(curr_cell, visited_cells)

            if direction is None:
                stack.pop()
            else:
                self.get_maze().carve_cell(curr_cell, direction)
                curr_cell.carve(direction)
                if direction == EDirection.NORTH:
                    stack.append(
                        self.get_maze().map[curr_cell.position.y - 1][
                            curr_cell.position.x
                        ]
                    )
                    updated_cells.append(
                        self.get_maze().map[curr_cell.position.y - 1][
                            curr_cell.position.x
                        ]
                    )
                elif direction == EDirection.EAST:
                    stack.append(
                        self.get_maze().map[curr_cell.position.y][
                            curr_cell.position.x + 1
                        ]
                    )
                    updated_cells.append(
                        self.get_maze().map[curr_cell.position.y][
                            curr_cell.position.x + 1
                        ]
                    )
                if direction == EDirection.SOUTH:
                    stack.append(
                        self.get_maze().map[curr_cell.position.y + 1][
                            curr_cell.position.x
                        ]
                    )
                    updated_cells.append(
                        self.get_maze().map[curr_cell.position.y + 1][
                            curr_cell.position.x
                        ]
                    )
                if direction == EDirection.WEST:
                    stack.append(
                        self.get_maze().map[curr_cell.position.y][
                            curr_cell.position.x - 1
                        ]
                    )
                    updated_cells.append(
                        self.get_maze().map[curr_cell.position.y][
                            curr_cell.position.x - 1
                        ]
                    )
            stack_len = len(stack)

        self.get_maze().status = Maze.Status.GENERATED

        if not self._get_perfect():
            self._make_imperfect()

        return updated_cells
