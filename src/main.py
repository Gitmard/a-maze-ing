from generator import RecursiveDivisionGenerator, Vec2
from parse import parse, Parsed, ParseError
from visualizer import visualize
from pydantic import ValidationError
import sys


def main() -> None:
    try:
        infos: Parsed = parse(
            "/home/vquetier/cc/m2/amazeing/feur/src/config.txt"
        )

    except ValidationError as e:
        print(e.errors()[0]["msg"])
        sys.exit(1)

    except ParseError as e:
        print(e)
        sys.exit(1)

    generator = RecursiveDivisionGenerator(
        infos.width,
        infos.height,
        Vec2(infos.entry[0], infos.entry[1]),
        Vec2(infos.exit[0], infos.exit[1]),
        seed=infos.seed
    )

    visualize(generator)


if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        print(f"an unexpected exception occured ({e})")
        sys.exit(1)
