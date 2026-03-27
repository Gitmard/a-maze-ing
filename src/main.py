#!/usr/bin/env python3

from typing import List

from generator import MazeGenerator, RecursiveDivisionGenerator, Vec2
from generator.AsciiMazeVisualizer import AsciiMazeVisualizer
from parse import parse, Parsed, ParseError
from visualizer import visualize
from pydantic import ValidationError
import sys


def test_is_perfect(generator: MazeGenerator) -> None:
    print("Running test_is_perfect")
    generator.generate()
    for y1 in range(generator.get_maze().height):
        for x1 in range(generator.get_maze().height):
            if (
                generator.get_maze().ft_pattern_start.x
                <= x1
                <= generator.get_maze().ft_pattern_end.x
                and generator.get_maze().ft_pattern_start.y
                <= y1
                <= generator.get_maze().ft_pattern_end.y
            ):
                continue
            for y2 in range(generator.get_maze().height):
                for x2 in range(generator.get_maze().width):
                    if (
                        generator.get_maze().ft_pattern_start.x
                        <= x2
                        <= generator.get_maze().ft_pattern_end.x
                        and generator.get_maze().ft_pattern_start.y
                        <= y2
                        <= generator.get_maze().ft_pattern_end.y
                    ) or (x1 == x2 and y1 == y2):
                        continue
                    generator.get_maze().start_pos = Vec2(x1, y1)
                    generator.get_maze().end_pos = Vec2(x2, y2)
                    generator.get_maze().solve()
                    solution = generator.get_solution()
                    try:
                        assert len(solution), (
                            f"Path with start=({generator.get_maze().start_pos}),"
                            + f" end=({generator.get_maze().end_pos}) has no solution\n"
                            + f"(pattern_start: {generator.get_maze().ft_pattern_start},"
                            + f" pattern_end: {generator.get_maze().ft_pattern_end})"
                        )
                        assert all(
                            not generator.get_maze()
                            .map[solution_coord[1]][solution_coord[0]]
                            .locked
                            for solution_coord in generator.get_maze().solution
                        ), (
                            f"Path with start=({generator.get_maze().start_pos}), end=({generator.get_maze().end_pos}) has a locked cell in its solution\n"
                            + f"(locked cells: {[cell for cell in generator.get_maze().solution if generator.get_maze().map[cell[1]][cell[0]].locked]})"
                        )
                    except AssertionError as err:
                        print("Maze: ")
                        AsciiMazeVisualizer.display_maze(generator.get_maze())
                        raise err
    print("test_is_perfect OK")


def main(filename: str, flags: List[str]) -> None:
    try:
        infos: Parsed = parse(filename)

    except ValidationError as e:
        print(e.errors()[0]["msg"])
        sys.exit(1)

    except ParseError as e:
        print(e)
        sys.exit(1)

    except OSError as e:
        print(e)

    generator = RecursiveDivisionGenerator(
        infos.width,
        infos.height,
        Vec2(infos.entry[0], infos.entry[1]),
        Vec2(infos.exit[0], infos.exit[1]),
        seed=infos.seed,
        add_ft_pattern=True,
    )

    if "--tests" in flags or "-t" in flags:
        if infos.perfect:
            test_is_perfect(generator)
    else:
        visualize(generator)
        generator.get_maze().solve()


if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[1:])
    except Exception as e:
        print(f"an unexpected exception occured ({e})")
        # sys.exit(1)
        raise e
