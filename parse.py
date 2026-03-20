from typing import Tuple
from pydantic import BaseModel, Field, model_validator, ValidationError


VALID_KEYS = {
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
    "SEED"
}


class ParseError(Exception):
    def __init__(self, msg: str = "Not specified"):
        super().__init__(f"ParseError: {msg}")


class Parsed(BaseModel):
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str = Field(min_length=1)
    perfect: bool
    seed: str

    @model_validator(mode="after")
    def validator(self):
        if any(coord < 0 for coord in self.entry):
            raise ValueError("Coordinates for entry should be positives")
        if any(coord < 0 for coord in self.exit):
            raise ValueError("Coordinates for exit should be positives")

        if self.entry[1] >= self.height:
            raise ValueError(
                "Coordinates for entry should be in the maze range"
            )

        if self.entry[0] >= self.width:
            raise ValueError(
                "Coordinates for entry should be in the maze range"
            )

        if self.exit[1] >= self.height:
            raise ValueError(
                "Coordinates for entry should be in the maze range"
            )

        if self.exit[0] >= self.width:
            raise ValueError(
                "Coordinates for entry should be in the maze range"
            )

        if self.entry == self.exit:
            raise ValueError(
                "Entry and exit should be different"
            )

        if self.width * self.height < 4 and self.perfect is True:
            raise ValueError(
                "Maze cannot be perfect with less than 4 cells"
            )

        return self


def parse_tuple(arg: str):
    return tuple(map(int, arg.split(',')))


def parse_bool(arg: str):
    match arg:
        case "True":
            return True
        case "False":
            return False
        case _:
            raise ParseError(
                f"PERFECT Argument should be True or False, not {arg}"
            )


FUNCTION_FOR_KEY = {
    "WIDTH": int,
    "HEIGHT": int,
    "ENTRY": parse_tuple,
    "EXIT": parse_tuple,
    "OUTPUT_FILE": lambda x: x,
    "PERFECT": parse_bool,
    "SEED": lambda x: x
}


def parse(filename):
    d = {}
    try:
        with open(filename) as f:
            for line in f:
                line = line.strip('\n')
                if line.startswith("#"):
                    continue
                if len(line) == 0:
                    continue
                try:
                    key, value = line.split("=")
                except Exception as e:
                    print(e)
                if key not in VALID_KEYS:
                    raise ParseError(f"Key is invalid ({key})")
                d[key.lower()] = FUNCTION_FOR_KEY[key](value)

    except Exception as e:
        print(f"Unexpected exception: {e}")
        return

    try:
        return Parsed(**d)
    except ValidationError as e:
        print(e)


if __name__ == "__main__":
    print(parse("/home/vquetier/cc/m2/amazeing/example.txt"))
