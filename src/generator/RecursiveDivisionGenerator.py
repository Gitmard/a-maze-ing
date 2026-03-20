from .EDirection import EDirection
from .MazeGenerator import MazeGenerator
from .Cell import Cell
from .Vec2 import Vec2
from typing import Generator, List, Optional, Union
from enum import IntEnum, auto
from copy import copy
from dataclasses import dataclass


class RecursiveDivisionGenerator(MazeGenerator):

    class Direction(IntEnum):
        NONE = auto()
        HORIZONTAL = auto()
        VERTICAL = auto()

    class Position(IntEnum):
        NONE = auto()
        TOP = auto()
        BOTTOM = auto()
        LEFT = auto()
        RIGHT = auto()

    @dataclass
    class DivisionFrame:
        position: "RecursiveDivisionGenerator.Position"
        direction: "RecursiveDivisionGenerator.Direction"
        local_height: int
        local_width: int
        subregion_pos: Vec2

    def __slice_random_vertical(
        self,
        current_frame: DivisionFrame
    ) -> List[DivisionFrame]:
        slice_x = int(
            self.__rng.randint(0, current_frame.local_width - 2)
        )
        return [
            RecursiveDivisionGenerator.DivisionFrame
            (
                position=RecursiveDivisionGenerator.Position.LEFT,
                direction=RecursiveDivisionGenerator.Direction.VERTICAL,
                local_width=(
                    current_frame.local_width - slice_x - 1
                    if (slice_x + 1) > current_frame.local_width // 2
                    else
                    slice_x + 1
                ),
                local_height=current_frame.local_height,
                subregion_pos=copy(current_frame.subregion_pos)
            ),
            RecursiveDivisionGenerator.DivisionFrame
            (
                position=RecursiveDivisionGenerator.Position.RIGHT,
                direction=RecursiveDivisionGenerator.Direction.VERTICAL,
                local_width=current_frame.local_width - slice_x - 1,
                local_height=current_frame.local_height,
                subregion_pos=Vec2(
                    x=current_frame.subregion_pos.x + slice_x + 1,
                    y=current_frame.subregion_pos.y
                )
            )
        ]

    def __slice_random_horizontal(
        self,
        current_frame: DivisionFrame
    ) -> List[DivisionFrame]:
        slice_y = int(
            self.__rng.randint(0, current_frame.local_height - 2)
        )
        return [
            RecursiveDivisionGenerator.DivisionFrame
            (
                position=RecursiveDivisionGenerator.Position.TOP,
                direction=RecursiveDivisionGenerator.Direction.HORIZONTAL,
                local_width=current_frame.local_width,
                local_height=(
                    current_frame.local_height - slice_y - 1
                    if (slice_y + 1) > current_frame.local_height // 2
                    else
                    slice_y + 1
                ),
                subregion_pos=copy(current_frame.subregion_pos)
            ),
            RecursiveDivisionGenerator.DivisionFrame
            (
                position=RecursiveDivisionGenerator.Position.BOTTOM,
                direction=RecursiveDivisionGenerator.Direction.HORIZONTAL,
                local_width=current_frame.local_width,
                local_height=current_frame.local_height - slice_y - 1,
                subregion_pos=Vec2(
                    x=current_frame.subregion_pos.x,
                    y=current_frame.subregion_pos.y + slice_y + 1
                )
            )
        ]

    def __slice_random(
        self,
        current_frame: DivisionFrame,
        direction: "RecursiveDivisionGenerator.Direction"
    ) -> List[DivisionFrame]:
        if direction == RecursiveDivisionGenerator.Direction.VERTICAL:
            return self.__slice_random_vertical(current_frame)
        else:
            return self.__slice_random_horizontal(current_frame)

    def __create_new_frames(
        self,
        current_frame: DivisionFrame
    ) -> List[DivisionFrame]:
        if current_frame.local_height > current_frame.local_width:
            return self.__slice_random(
                current_frame,
                RecursiveDivisionGenerator.Direction.HORIZONTAL
            )

        if current_frame.local_height < current_frame.local_width:
            return self.__slice_random(
                current_frame,
                RecursiveDivisionGenerator.Direction.VERTICAL
            )

        return self.__slice_random(
            current_frame,
            (
                RecursiveDivisionGenerator.Direction.VERTICAL
                if self._get_rng().randint(0, 1) >= 0.5
                else
                RecursiveDivisionGenerator.Direction.HORIZONTAL
            )
        )

    def __add_vertical_wall(
        self,
        current_frame: DivisionFrame
    ) -> List[Cell]:
        edited_cells: List[Cell] = []
        wall_x = current_frame.subregion_pos.x + current_frame.local_width - 1
        opening_y = self._get_rng().randint(
            current_frame.subregion_pos.y,
            current_frame.local_height - 2
        )
        while self.get_maze().map[opening_y][wall_x].locked:
            opening_y = self._get_rng().randint(
                current_frame.subregion_pos.y,
                current_frame.local_height - 2
            )
        for y in range(current_frame.local_height):
            curr_cells = [
                self.get_maze().map[y][wall_x],
                self.get_maze().map[y][wall_x + 1]
            ]
            curr_cells[0].enclose(EDirection.EAST)
            curr_cells[1].enclose(EDirection.WEST)
            edited_cells.extend(curr_cells)
        self.get_maze()[opening_y][wall_x].carve(EDirection.EAST)
        self.get_maze()[opening_y][wall_x + 1].carve(EDirection.WEST)
        return edited_cells

    def __add_horizontal_wall(
        self,
        current_frame: DivisionFrame
    ) -> List[Cell]:
        edited_cells: List[Cell] = []
        wall_y = current_frame.subregion_pos.y + current_frame.local_height - 1
        opening_x = self._get_rng().randint(
            current_frame.subregion_pos.x,
            current_frame.local_width - 2
        )
        while self.get_maze().map[wall_y][opening_x].locked:
            opening_x = self._get_rng().randint(
                current_frame.subregion_pos.x,
                current_frame.local_width - 2
            )
        for x in range(current_frame.local_width):
            curr_cells = [
                self.get_maze().map[wall_y][x],
                self.get_maze().map[wall_y + 1][x]
            ]
            curr_cells[0].enclose(EDirection.SOUTH)
            curr_cells[1].enclose(EDirection.NORTH)
            edited_cells.extend(curr_cells)
        self.get_maze()[wall_y][opening_x].carve(EDirection.SOUTH)
        self.get_maze()[wall_y][opening_x + 1].carve(EDirection.NORTH)
        return edited_cells

    def __add_wall(
        self,
        current_frame: DivisionFrame
    ) -> List[Cell]:
        if (
            current_frame.direction
            == RecursiveDivisionGenerator.Direction.VERTICAL
        ):
            return self.__add_vertical_wall(current_frame)
        else:
            return self.__add_horizontal_wall(current_frame)

    def generate(
        self,
        tick_count: int = -1,
        seed: Optional[str] = None
    ) -> Union[
        List[List[Cell]],
        Generator[List[Cell], None, None],
    ]:
        """
            stack = [full_maze]
            while stack:
                curr = stack.pop()
                if max(curr.height, curr.width) <= 2:
                    continue

                decide which slice

                slice_random()

                create_wall

                stack.append(slice1)
                stack.append(slice2)
        """
        if seed is not None:
            self._get_rng().seed(seed)

        stack: List[RecursiveDivisionGenerator.DivisionFrame] = [
            RecursiveDivisionGenerator.DivisionFrame(
                position=(
                    RecursiveDivisionGenerator.Position.NONE
                ),
                direction=(
                    RecursiveDivisionGenerator.Direction.NONE
                ),
                local_height=self.get_maze().height,
                local_width=self.get_maze().width,
                subregion_pos=Vec2(0, 0)
            )
        ]

        updated_cells: List[Cell] = []
        while len(stack):
            current_frame = stack.pop()

            if max(
                current_frame.local_height,
                current_frame.local_width
            ) <= 2:
                continue

            new_frames: List[
                RecursiveDivisionGenerator.DivisionFrame
            ] = self.__create_new_frames(current_frame)

            updated_cells.extend(
                self.__add_wall(current_frame)
            )

            stack.extend(new_frames)

        return updated_cells
