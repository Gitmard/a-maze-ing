from copy import copy
from .MazeGenerator import MazeGenerator
from .Cell import Cell
from .EDirection import EDirection
from .Vec2 import Vec2
from typing import Generator, List, Union, TypedDict, Dict
from enum import IntEnum, auto


class RescursiveDivisionGenerator(MazeGenerator):

    class EDivisionDirection(IntEnum):
        HORIZONTAL: int = auto()
        VERTICAL: int = auto()

    class EDivisionPosition(IntEnum):
        TOP: int = auto()
        BOTTOM: int = auto()
        LEFT: int = auto()
        RIGHT: int = auto()

    class DivisionFrameDict(TypedDict):
        position: int
        direction: int
        local_height: int
        local_width: int
        subregion_pos: Vec2

    def __horizontal_division(
        self,
        current_local_width: int,
        current_local_height: int,
        current_subregion_pos: Vec2
    ) -> List["RescursiveDivisionGenerator.DivisionFrameDict"]:
        return [
            {
                "direction":
                    RescursiveDivisionGenerator.EDivisionDirection.HORIZONTAL,
                "local_height": current_local_height,
                "local_width": current_local_width,
                "position":
                    RescursiveDivisionGenerator.EDivisionPosition.TOP,
                "subregion_pos": copy(current_subregion_pos)

            }, {
                "direction":
                    RescursiveDivisionGenerator.EDivisionDirection.HORIZONTAL,
                "local_height": current_local_height,
                "local_width": current_local_width,
                "position":
                    RescursiveDivisionGenerator.EDivisionPosition.BOTTOM,
                "subregion_pos": copy(current_subregion_pos)
            }
        ]

    def __vertical_division(
        self,
        current_local_width: int,
        current_local_height: int,
        current_subregion_pos: Vec2
    ) -> List[Dict[str, int]]:
        return [
            {
                "direction":
                    RescursiveDivisionGenerator.EDivisionDirection.VERTICAL,
                "local_height": current_local_height,
                "local_width": current_local_width,
                "position":
                    RescursiveDivisionGenerator.EDivisionPosition.LEFT,
                "subregion_pos": copy(current_subregion_pos)
            }, {
                "direction":
                    RescursiveDivisionGenerator.EDivisionDirection.VERTICAL,
                "local_height": current_local_height,
                "local_width": current_local_width,
                "position":
                    RescursiveDivisionGenerator.EDivisionPosition.RIGHT,
                "subregion_pos": copy(current_subregion_pos)
            }
        ]

    def __build_divisions_stack(
        self
    ) -> List["RescursiveDivisionGenerator.DivisionFrameDict"]:
        divisions_stack: List[
            RescursiveDivisionGenerator.DivisionFrameDict
        ] = []
        current_local_height: int = self.get_maze().height
        current_local_width: int = self.get_maze().width
        current_subregion_pos = Vec2(0, 0)


        while current_local_height > 4 and current_local_width > 4:
            if current_local_width > current_local_height:
                current_local_width /= 2
                divisions_stack.extend(
                    self.__vertical_division(
                        current_local_width,
                        current_local_height,
                        current_subregion_pos
                    )
                )
            else:
                current_local_height /= 2
                divisions_stack.extend(
                    self.__horizontal_division(
                        current_local_width,
                        current_local_height,
                        current_subregion_pos
                    )
                )




        while current_local_height > 4:
            current_local_height /= 2
            divisions_stack.extend(
                self.__horizontal_division(
                    current_local_width,
                    current_local_height,
                    current_subregion_pos
                )
            )
        while current_local_width > 4:
            current_local_width /= 2
            divisions_stack.extend(
                self.__vertical_division(
                    current_local_width,
                    current_local_height,
                    current_subregion_pos
                )
            )
        return divisions_stack

    def __add_vertical_wall(
        self,
        length: int,
        line_x: int,
    ) -> List[Cell]:
        pass

    def __add_horizontal_wall(
        self,
        length: int,
        line_y: int,
    ):
        pass

    def __exec_division_frame(
        self,
        division_frame: "RescursiveDivisionGenerator.DivisionFrameDict"
    ) -> List[Cell]:
        rng = self._get_rng()
        line_length: int = 0

        if (
            division_frame["direction"] ==
            RescursiveDivisionGenerator.EDivisionDirection.HORIZONTAL
        ):
            line_length = division_frame["local_width"]
            line_y = rng.randint(division_frame["local_height"])
            self.__add_horizontal_wall(
                line_length,
                line_y
            )
        else:
            line_length = division_frame["local_height"]
            line_x = rng.randint(division_frame["local_width"])
            self.__add_vertical_wall(
                line_length,
                line_x
            )

    def __recursive_division(self) -> Generator[List[Cell], None, None]:
        divisions_stack: List[
            RescursiveDivisionGenerator.DivisionFrameDict
        ] = self.__build_divisions_stack()

    def __generate_full_maze(self) -> List[List[Cell]]:
        raise NotImplementedError(
            "Method __generate_full_maze of class" +
            " RescursiveDivisionGenerator (child of MazeGenerator)" +
            " not yet implemented"
        )

    def generate(self, tick_count: int = -1, seed: str = None) -> Union[
        List[List[Cell]],
        Generator[List[Cell], None, None],
    ]:
        if tick_count == -1:
            return self.__generate_        stack = [full_maze]
full_maze()


        """
            stack = [full_maze]
            while stack:
                curr = stack.pop()
                if max(curr.height, curr.width) <= 2:
                    continue

                decide which slice

                slice_random()

                create_wall

                create two regions

                stack.append(reg1)
                stack.append(reg2)
        """

        yield None
        return None
