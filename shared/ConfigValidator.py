from typing import Optional
from mazegen.Vec2 import Vec2
from shared.InvalidConfigException import InvalidConfigException


class ConfigValidator:

    @staticmethod
    def __validate_maze_dimensions(height: int, width: int) -> None:
        if not isinstance(height, int):
            raise InvalidConfigException(
                "Height must be an integer"
            )
        if not isinstance(width, int):
            raise InvalidConfigException(
                "Width must be an integer"
            )
        if height <= 1:
            raise InvalidConfigException(
                "Height must be > 1"
            )
        if width <= 1:
            raise InvalidConfigException(
                "Width must be > 1"
            )

    @staticmethod
    def __validate_entry_exit(
        entry: Vec2,
        exit: Vec2,
        width: int,
        height: int,
    ) -> None:
        if not isinstance(entry, Vec2):
            raise InvalidConfigException(
                "Entry must be a Vec2 point"
            )
        if not isinstance(exit, Vec2):
            raise InvalidConfigException(
                "Exit must be a Vec2 point"
            )
        if entry.x == exit.x and entry.y == exit.y:
            raise InvalidConfigException(
                "Entry and exit must be different"
            )
        if not (0 <= entry.x < width):
            raise InvalidConfigException(
                f"Entry.x must be >= 0 and < width (got {entry.x}, width={width})"
            )
        if not (0 <= exit.x < width):
            raise InvalidConfigException(
                f"Exit.x must be >= 0 and < width (got {exit.x}, width={width})"
            )
        if not (0 <= entry.y < height):
            raise InvalidConfigException(
                f"Entry.y must be >= 0 and < height (got {entry.y}, height={height})"
            )
        if not (0 <= exit.y < height):
            raise InvalidConfigException(
                f"Exit.y must be >= 0 and < height (got {exit.y}, height={height})"
            )

    @staticmethod
    def __validate_perfect(perfect: bool) -> None:
        if type(perfect) is not bool:
            raise InvalidConfigException(
                "Perfect must be a boolean"
            )

    @staticmethod
    def __validate_output_file(output_file: str) -> None:
        if not isinstance(output_file, str):
            raise InvalidConfigException(
                "Output file must be a string"
            )
        if not len(output_file.strip()):
            raise InvalidConfigException(
                "Output file cannot be an empty string"
            )

    @staticmethod
    def __validate_seed(seed: Optional[str]) -> None:
        if seed is not None and not isinstance(seed, str):
            raise InvalidConfigException(
                "Seed must be None or a string"
            )
        if isinstance(seed, str) and not len(seed):
            raise InvalidConfigException(
                "Seed cannot be an empty string"
            )

    @classmethod
    def validate(
        cls,
        height: int,
        width: int,
        entry: Vec2,
        exit: Vec2,
        perfect: bool,
        output_file: str,
        seed: Optional[str]
    ) -> None:
        cls.__validate_maze_dimensions(
            height=height,
            width=width)
        cls.__validate_entry_exit(
            entry=entry,
            exit=exit,
            height=height,
            width=width)
        cls.__validate_perfect(perfect)
        cls.__validate_output_file(output_file)
        cls.__validate_seed(seed)
