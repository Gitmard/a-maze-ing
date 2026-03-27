from generator.Maze import Maze
from generator.EDirection import EDirection
from generator.MazeGenerator import MazeGenerator
from generator.Cell import Cell
from typing import List, Optional, Set


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

        return updated_cells
