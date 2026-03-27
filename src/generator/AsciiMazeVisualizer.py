from typing import List, Set, Tuple

from generator.Cell import Cell
from generator.EDirection import EDirection
from generator.Maze import Maze
from colorama import Back

RESET = Back.RESET
BG_LOCKED = Back.WHITE
BG_START = Back.GREEN
BG_END = Back.BLUE
BG_SOLUTION = Back.RED


def find_neighbor(maze: List[List[int]], cell: Tuple[Cell]):
    x, y = cell

    directions = {1: (0, -1), 2: (1, 0), 4: (0, 1), 8: (-1, 0)}

    for dir, move in directions.items():
        move_x, move_y = move
        if not (maze[y][x].walls & dir):
            yield (x + move_x, y + move_y)


def find_paths(
    maze: List[List[int]], entry: Tuple[int, int], exit: Tuple[int, int]
) -> Set[Tuple[int, int]]:
    path_count = 0
    explored_set = set()

    path_cells = set()

    def dfs(curr_cell: Tuple[int, int]) -> bool:
        nonlocal path_count
        nonlocal explored_set

        if curr_cell == exit:
            path_count += 1
            path_cells.add(curr_cell)
            return True

        explored_set.add(curr_cell)

        ret = False

        for n in find_neighbor(maze, curr_cell):
            if n not in explored_set:
                if dfs(n):
                    path_cells.add(curr_cell)
                    ret = True

        explored_set.remove(curr_cell)

        return ret

    dfs(entry)
    return path_cells


class AsciiMazeVisualizer:

    @staticmethod
    def display_maze(maze: Maze) -> None:
        width = maze.width
        height = maze.height

        solutions = (
            find_paths(
                maze.map,
                (maze.start_pos.x, maze.start_pos.y),
                (maze.end_pos.x, maze.end_pos.y),
            )
            if maze.status == Maze.Status.GENERATED
            else set()
        )

        top_line_coords = "    "
        for i in range(width):
            top_line_coords += f" {i:02} "
        print(top_line_coords)
        for y in range(height):
            top_row = "    "
            for x in range(width):
                cell = maze.map[y][x]
                has_north = bool(cell.walls & EDirection.NORTH.value)
                top_row += "+" + ("---" if has_north else "   ")
            print(top_row + "+")

            mid_row = f" {y:02} "
            for x in range(width):
                cell = maze.map[y][x]
                has_west = bool(cell.walls & EDirection.WEST.value)
                cell_bg = (
                    BG_LOCKED
                    if cell.locked
                    else (
                        BG_START
                        if (
                            maze.start_pos.x == cell.position.x
                            and maze.start_pos.y == y
                        )
                        else (
                            BG_END
                            if (
                                maze.end_pos.x == cell.position.x
                                and maze.end_pos.y == cell.position.y
                            )
                            else (
                                BG_SOLUTION
                                if (
                                    any(
                                        cell.position.x == solution_cell[0]
                                        and cell.position.y == solution_cell[1]
                                        for solution_cell in solutions
                                    )
                                )
                                else ""
                            )
                        )
                    )
                )
                mid_row += ("|" if has_west else " ") + cell_bg + "   " + RESET
            last_cell = maze.map[y][width - 1]
            has_east = bool(last_cell.walls & EDirection.EAST.value)
            print(mid_row + ("|" if has_east else " "))

        bottom_row = "    "
        for x in range(width):
            cell = maze.map[height - 1][x]
            has_south = bool(cell.walls & EDirection.SOUTH.value)
            bottom_row += "+" + ("---" if has_south else "   ")
        print(bottom_row + "+")
