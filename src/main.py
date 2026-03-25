#!/usr/bin/env python3

from generator import RecursiveDivisionGenerator, Vec2
from generator.AsciiMazeVisualizer import AsciiMazeVisualizer
from parse import parse, Parsed, ParseError
from visualizer import visualize
from pydantic import ValidationError
import sys


def main(filename: str) -> None:
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
    # generator.generate(show_progress=False)
    # AsciiMazeVisualizer.display_maze(generator.get_maze())
    visualize(generator)


if __name__ == "__main__":
    try:
        main(sys.argv[1])

    except Exception as e:
        print(f"an unexpected exception occured ({e})")
        # sys.exit(1)
        raise e
