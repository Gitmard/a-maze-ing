#!/usr/bin/env python3

from generator.Maze import Maze
from generator.RecursiveDivisionGenerator import RecursiveDivisionGenerator
from generator.EDirection import EDirection


def display_maze(maze: Maze) -> None:
    width = maze.width
    height = maze.height

    for y in range(height):
        # Ligne du haut de chaque rangée de cellules
        top_row = ""
        for x in range(width):
            cell = maze.map[y][x]
            has_north = bool(cell.walls & EDirection.NORTH.value)
            top_row += "+" + ("---" if has_north else "   ")
        print(top_row + "+")

        # Ligne du milieu (murs est/ouest + contenu)
        mid_row = ""
        for x in range(width):
            cell = maze.map[y][x]
            has_west = bool(cell.walls & EDirection.WEST.value)
            mid_row += ("|" if has_west else " ") + "   "
        # Mur est de la dernière cellule
        last_cell = maze.map[y][width - 1]
        has_east = bool(last_cell.walls & EDirection.EAST.value)
        print(mid_row + ("|" if has_east else " "))

    # Ligne du bas du maze
    bottom_row = ""
    for x in range(width):
        cell = maze.map[height - 1][x]
        has_south = bool(cell.walls & EDirection.SOUTH.value)
        bottom_row += "+" + ("---" if has_south else "   ")
    print(bottom_row + "+")


if __name__ == "__main__":
    generator = RecursiveDivisionGenerator(width=20, height=10)
    generator.generate(seed="test")
    display_maze(generator.get_maze())
