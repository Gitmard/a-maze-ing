#!/usr/bin/env python3

from mazegen import DepthFirstSearchGenerator, Vec2
from mazegen.GeneratorException import GeneratorException
from src.parse import parse, Parsed, ParseError
from src.visualizer import visualize
from pydantic import ValidationError
import sys


def main(filename: str) -> None:
    try:
        infos: Parsed = parse(filename)

    except ValidationError as e:
        print(e.errors()[0]["msg"])
        return

    except ParseError as e:
        print(e)
        return

    except OSError as e:
        print(e)
        return

    try:
        generator = DepthFirstSearchGenerator(
            infos.width,
            infos.height,
            Vec2(infos.entry[0], infos.entry[1]),
            Vec2(infos.exit[0], infos.exit[1]),
            seed=infos.seed,
            output_file=infos.output_file,
            is_perfect=infos.perfect,
            locked_cells=[
                [1, 0, 0, 0, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 1, 1],
            ]
        )

    except GeneratorException as e:
        print(f"An error occured during maze generation ({e})")
        return
    try:
        visualize(generator)

    except GeneratorException as e:
        print(f"An error occured during maze generation ({e})")


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            print(
                "Usage: python3 a_maze_ing.py [config_file] /",
                "make run /",
                "make run CONFIG=[config_file]"
            )
            sys.exit(1)

        main(sys.argv[1])

    except Exception as e:
        print(f"an unexpected exception occured ({e})")
        sys.exit(1)
