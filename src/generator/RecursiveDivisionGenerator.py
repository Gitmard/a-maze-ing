from .MazeGenerator import MazeGenerator
from .Cell import Cell
from .EDirection import EDirection
from typing import Generator, List, Union
from enum import Enum


class RescursiveDivisionGenerator(MazeGenerator):

    class EDivisionDirection(Enum):
        HORIZONTAL = 1
        VERTICAL = 2

    def __generate_full_maze(self) -> List[List[Cell]]:
        raise NotImplementedError(
            "Method __generate_full_maze of class" +
            " RescursiveDivisionGenerator (child of MazeGenerator)" +
            " not yet implemented"
        )

    def generate(self, tick_count: int = -1) -> Union[
        List[List[Cell]],
        Generator[List[Cell], None, None]
    ]:
        if tick_count == -1:
            return self.__generate_full_maze()
        yield None
        return None
