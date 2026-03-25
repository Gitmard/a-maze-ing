from generator.EDirection import EDirection
from generator.Maze import Maze

RESET = "\033[0m"
BG_WHITE = "\033[47m"


class AsciiMazeVisualizer:

    @staticmethod
    def display_maze(maze: Maze) -> None:
        width = maze.width
        height = maze.height

        for y in range(height):
            top_row = ""
            for x in range(width):
                cell = maze.map[y][x]
                has_north = bool(cell.walls & EDirection.NORTH.value)
                top_row += "+" + ("---" if has_north else "   ")
            print(top_row + "+")

            mid_row = ""
            for x in range(width):
                cell = maze.map[y][x]
                has_west = bool(cell.walls & EDirection.WEST.value)
                cell_bg = BG_WHITE if cell.locked else ""
                mid_row += ("|" if has_west else " ") + cell_bg + "   " + RESET
            last_cell = maze.map[y][width - 1]
            has_east = bool(last_cell.walls & EDirection.EAST.value)
            print(mid_row + ("|" if has_east else " "))

        bottom_row = ""
        for x in range(width):
            cell = maze.map[height - 1][x]
            has_south = bool(cell.walls & EDirection.SOUTH.value)
            bottom_row += "+" + ("---" if has_south else "   ")
        print(bottom_row + "+")
