from generator.EDirection import EDirection
from generator.Maze import Maze
from colorama import Back

RESET = Back.RESET
BG_LOCKED = Back.WHITE
BG_START = Back.GREEN
BG_END = Back.BLUE
BG_SOLUTION = Back.RED


class AsciiMazeVisualizer:

    @staticmethod
    def display_maze(maze: Maze) -> None:
        width = maze.width
        height = maze.height

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
                                        and cell.position.y
                                        == solution_cell[1]
                                        for solution_cell in maze.solution
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
