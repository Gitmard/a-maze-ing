"""Configuration file parser for maze generation parameters.

Reads a simple ``KEY=VALUE`` text file and validates the result
into a :class:`Parsed` model using Pydantic.
"""

from typing import Callable, Dict, Set, Tuple, cast

from typing_extensions import TypedDict

from pydantic import BaseModel, Field, model_validator


class ParseError(Exception):
    """Raised when the configuration file is malformed.

    Args:
        msg: Human-readable description of the problem.
    """

    def __init__(self, msg: str = "Not specified") -> None:
        super().__init__(f"ParseError: {msg}")


class Parsed(BaseModel):
    """Validated maze configuration.

    Attributes:
        width: Number of columns (>= 1).
        height: Number of rows (>= 1).
        entry: ``(x, y)`` coordinates of the maze entrance.
        exit: ``(x, y)`` coordinates of the maze exit.
        output_file: Path for the generated output.
        perfect: Whether the maze must be perfect (no loops).
        seed: RNG seed string.
    """

    width: int = Field(ge=1)
    height: int = Field(ge=1)
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str = Field(min_length=1)
    perfect: bool
    seed: str

    @model_validator(mode="after")
    def validate_coords(self) -> "Parsed":
        """Check that entry/exit are in-bounds and distinct."""
        if any(coord < 0 for coord in self.entry):
            raise ValueError(
                "Coordinates for entry should be positive"
            )
        if any(coord < 0 for coord in self.exit):
            raise ValueError(
                "Coordinates for exit should be positive"
            )

        if (
            self.entry[0] >= self.width
            or self.entry[1] >= self.height
        ):
            raise ValueError(
                "Coordinates for entry should be in the "
                "maze range"
            )

        if (
            self.exit[0] >= self.width
            or self.exit[1] >= self.height
        ):
            raise ValueError(
                "Coordinates for exit should be in the "
                "maze range"
            )

        if self.entry == self.exit:
            raise ValueError(
                "Entry and exit should be different"
            )

        if self.width * self.height < 4 and self.perfect:
            raise ValueError(
                "Maze cannot be perfect with less than 4 cells"
            )

        return self


class ParsedDict(TypedDict):
    """Intermediate typed dict matching :class:`Parsed` fields."""

    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool
    seed: str


def parse_tuple(arg: str) -> Tuple[int, int]:
    """Parse a ``'x,y'`` string into an integer 2-tuple.

    Args:
        arg: Comma-separated pair of integers.

    Returns:
        The parsed ``(x, y)`` tuple.

    Raises:
        ValueError: If *arg* does not contain exactly two ints.
    """
    parts = arg.split(",")
    if len(parts) != 2:
        raise ParseError(
            f"Expected 'x,y' coordinate pair, got '{arg}'"
        )
    return (int(parts[0]), int(parts[1]))


def parse_bool(arg: str) -> bool:
    """Parse ``'True'`` / ``'False'`` into a boolean.

    Args:
        arg: Literal ``"True"`` or ``"False"``.

    Returns:
        The corresponding boolean value.

    Raises:
        ParseError: If *arg* is neither ``"True"`` nor
            ``"False"``.
    """
    match arg:
        case "True":
            return True
        case "False":
            return False
        case _:
            raise ParseError(
                "PERFECT argument should be True or "
                f"False, not {arg}"
            )


VALID_KEYS: Set[str] = {
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
    "SEED",
}

_identity: Callable[[str], str] = lambda x: x

FUNCTION_FOR_KEY: Dict[str, Callable[..., object]] = {
    "WIDTH": int,
    "HEIGHT": int,
    "ENTRY": parse_tuple,
    "EXIT": parse_tuple,
    "OUTPUT_FILE": _identity,
    "PERFECT": parse_bool,
    "SEED": _identity,
}


def parse(filename: str) -> Parsed:
    """Read and validate a maze configuration file.

    The file format is one ``KEY=VALUE`` pair per line.
    Lines starting with ``#`` and blank lines are ignored.

    Args:
        filename: Path to the configuration file.

    Returns:
        A validated :class:`Parsed` instance.

    Raises:
        ParseError: If the file contains an invalid key or
            a malformed line.
        FileNotFoundError: If *filename* does not exist.
        pydantic.ValidationError: If the parsed values fail
            model validation.
    """
    values: Dict[str, object] = {}

    with open(filename) as f:
        for raw_line in f:
            line = raw_line.strip("\n")

            if line.startswith("#") or len(line) == 0:
                continue

            if "=" not in line:
                raise ParseError(
                    f"Malformed line (missing '='): {line}"
                )

            key, value = line.split("=", maxsplit=1)

            if key not in VALID_KEYS:
                raise ParseError(f"Key is invalid ({key})")

            values[key.lower()] = FUNCTION_FOR_KEY[key](value)

    typed: ParsedDict = {
        "width": cast(int, values["width"]),
        "height": cast(int, values["height"]),
        "entry": cast(Tuple[int, int], values["entry"]),
        "exit": cast(Tuple[int, int], values["exit"]),
        "output_file": cast(str, values["output_file"]),
        "perfect": cast(bool, values["perfect"]),
        "seed": cast(str, values["seed"]),
    }

    return Parsed(**typed)
