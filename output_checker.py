#!/usr/bin/env python3

from typing import List, Tuple
from sys import argv


def parse(filename: str):
    maze = []
    entry = None
    exit = None
    last_line = None
    with open(filename) as f:
        for line in f:
            line = line.strip('\n')

            if last_line is None:
                last_line = line
                continue

            if len(last_line) == 0:
                last_line = line
                continue

            if last_line.startswith('('):
                last_line = last_line.strip('()')
                x, y = tuple(map(int, last_line.split(',')))

                if entry is not None:
                    exit = (x, y)

                else:
                    entry = (x, y)

                last_line = line
                continue

            row = []
            for c in last_line:
                row.append(int(c, base=16))

            maze.append(row)

            last_line = line

    return maze, entry, exit


def find_neighbor(maze: List[List[int]], cell: Tuple[int, int]):
    x, y = cell

    directions = {
        1: (0, -1),
        2: (1, 0),
        4: (0, 1),
        8: (-1, 0)
    }

    for dir, move in directions.items():
        move_x, move_y = move
        if not (maze[y][x] & dir):
            yield (x + move_x, y + move_y)


def find_paths(maze: List[List[int]],
               entry: Tuple[int, int],
               exit: Tuple[int, int]):
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

    print(f"Nombre de paf: {path_count}")

    if path_count >= 2:
        print("Imparfait sale nab de merde")

    elif path_count == 1:
        print("Parfait bello bito")

    else:
        print("Insolvable le maze carrement grande pute")

    print("voici les multiples chemins (sans wall mdrrr ma bite jfais un visu asci)")

    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if (x, y) in path_cells:
                print('#', end='')

            else:
                print('.', end='')

        print()


if __name__ == "__main__":
    if len(argv) != 2:
        print("Usage: python [script.py] [maze_file.py]")

    try:
        maze, entry, exit = parse(argv[1])
        find_paths(maze, entry, exit)

    except OSError as e:
        print(e)

    except Exception as e:
        print(e)
