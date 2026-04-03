from typing import Optional
from mazegen.Vec2 import Vec2
from config_validation.InvalidConfigException import InvalidConfigException


class ConfigValidator:
    """Validate maze configuration parameters before generation."""

    @staticmethod
    def __validate_maze_dimensions(height: int, width: int) -> None:
        """Validate that height and width are positive integers.

        Args:
            height: Number of rows in the maze.
            width: Number of columns in the maze.

        Raises:
            InvalidConfigException: If either value is not an integer
                or is less than 1.
        """
        if not isinstance(height, int):
            raise InvalidConfigException(
                "Height must be an integer"
            )
        if not isinstance(width, int):
            raise InvalidConfigException(
                "Width must be an integer"
            )
        if height < 1:
            raise InvalidConfigException(
                "Height must be >= 1"
            )
        if width < 1:
            raise InvalidConfigException(
                "Width must be >= 1"
            )

    @staticmethod
    def __validate_entry_exit(
        entry: Vec2,
        exit: Vec2,
        width: int,
        height: int,
    ) -> None:
        """Validate that entry and exit are distinct Vec2 points within bounds.

        Args:
            entry: Maze entry coordinates.
            exit: Maze exit coordinates.
            width: Number of columns in the maze.
            height: Number of rows in the maze.

        Raises:
            InvalidConfigException: If either point is not a Vec2, if they
                are identical, or if they fall outside the grid.
        """
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
                "Entry.x must be >= 0 and < width"
            )
        if not (0 <= exit.x < width):
            raise InvalidConfigException(
                "Exit.x must be >= 0 and < width"
            )
        if not (0 <= entry.y < height):
            raise InvalidConfigException(
                "Entry.y must be >= 0 and < height"
            )
        if not (0 <= exit.y < height):
            raise InvalidConfigException(
                "Exit.y must be >= 0 and < height"
            )

    @staticmethod
    def __validate_perfect(perfect: bool) -> None:
        """Validate that perfect is a boolean.

        Args:
            perfect: Whether the maze should be perfect.

        Raises:
            InvalidConfigException: If the value is not a bool.
        """
        if type(perfect) is not bool:
            raise InvalidConfigException(
                "Perfect must be a boolean"
            )

    @staticmethod
    def __validate_output_file(output_file: str) -> None:
        """Validate that output_file is a non-empty string.

        Args:
            output_file: Path for the output file.

        Raises:
            InvalidConfigException: If the value is not a string
                or is empty/whitespace.
        """
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
        """Validate that seed is either None or a non-empty string.

        Args:
            seed: RNG seed value.

        Raises:
            InvalidConfigException: If seed is a non-string truthy value
                or an empty string.
        """
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
        """Run all configuration validations.

        Args:
            height: Number of rows in the maze.
            width: Number of columns in the maze.
            entry: Maze entry coordinates.
            exit: Maze exit coordinates.
            perfect: Whether the maze should be perfect.
            output_file: Path for the output file.
            seed: RNG seed value, or None.

        Raises:
            InvalidConfigException: If any parameter is invalid.
        """
        cls.__validate_maze_dimensions(
            height=height,
            width=width
        )
        cls.__validate_entry_exit(
            entry=entry,
            exit=exit,
            height=height,
            width=width
        )
        cls.__validate_perfect(perfect)
        cls.__validate_output_file(output_file)
        cls.__validate_seed(seed)
