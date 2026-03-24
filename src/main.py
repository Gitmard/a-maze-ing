#!/usr/bin/env python3

from sys import argv
from typing import Optional

from generator.AsciiMazeVisualizer import AsciiMazeVisualizer
from generator.RecursiveDivisionGenerator import RecursiveDivisionGenerator


def main() -> None:
    seed: Optional[str] = None
    width = 20
    height = 10
    if len(argv) > 1:
        seed = argv[1]
    try:
        if len(argv) > 3:
            width = int(argv[2])
            height = int(argv[3])
    except ValueError:
        print(
            "Invalid parameters, usage: python3 main.py <seed> <width>",
            "<height>"
        )
    generator = RecursiveDivisionGenerator(
        seed=seed,
        width=width,
        height=height
    )
    generator.generate()
    # AsciiMazeVisualizer.display_maze(generator.get_maze())



if __name__ == "__main__":
    main()
