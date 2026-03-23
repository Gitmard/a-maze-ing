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
        HORIZONTAL = auto()
        VERTICAL = auto()

    class Position(IntEnum):
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
            self._get_rng().randint(0, current_frame.local_width - 2)
        )
        return [
            RecursiveDivisionGenerator.DivisionFrame
            (
                position=RecursiveDivisionGenerator.Position.LEFT,
                direction=RecursiveDivisionGenerator.Direction.VERTICAL,
                local_width=slice_x + 1,
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
            self._get_rng().randint(0, current_frame.local_height - 2)
        )
        return [
            RecursiveDivisionGenerator.DivisionFrame
            (
                position=RecursiveDivisionGenerator.Position.TOP,
                direction=RecursiveDivisionGenerator.Direction.HORIZONTAL,
                local_width=current_frame.local_width,
                local_height=slice_y + 1,
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

        # Choose the direction of the slice
        # If the current slice is taller than it is wide,
        # Slice horizontally
        if current_frame.local_height > current_frame.local_width:
            return self.__slice_random(
                current_frame,
                RecursiveDivisionGenerator.Direction.HORIZONTAL
            )

        # The current slice is wider than it is tall,
        # Slice vertically
        if current_frame.local_height < current_frame.local_width:
            return self.__slice_random(
                current_frame,
                RecursiveDivisionGenerator.Direction.VERTICAL
            )

        # The current slice is as wide as it is tall
        # Pick a random direction
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

        # The wall's x coordinate is constant
        wall_x = current_frame.subregion_pos.x + current_frame.local_width - 1

        # Choose a random coordinate for the opening
        # We bound the coordinate from the beginning to the height - 2
        # For a slice of width 10, the opening will be between y=0 and y=8
        # Pick a new coordinate if we chose a locked cell
        # TODO: Use a set of available coordinates, removing from said set when we pick
        # This would avoid an infinite loop in there is no available cell
        opening_y = -1
        while (
            opening_y == -1
            or self.get_maze().map[opening_y][wall_x].locked
            or self.get_maze().map[opening_y][wall_x + 1].locked
        ):
            opening_y = self._get_rng().randint(
                current_frame.subregion_pos.y,
                current_frame.subregion_pos.y + current_frame.local_height - 2
            )

        # Loop through the wall's height
        for y in range(
            current_frame.subregion_pos.y,
            current_frame.subregion_pos.y + current_frame.local_height
        ):
            curr_cells = [
                self.get_maze().map[y][wall_x],
                self.get_maze().map[y][wall_x + 1]
            ]

            # Update the cells adjacent to the wall
            curr_cells[0].enclose(EDirection.EAST)
            curr_cells[1].enclose(EDirection.WEST)
            edited_cells.extend(curr_cells)

        # Carve the cells with the opening
        self.get_maze().map[opening_y][wall_x].carve(EDirection.EAST)
        self.get_maze().map[opening_y][wall_x + 1].carve(EDirection.WEST)
        return edited_cells

    def __add_horizontal_wall(
        self,
        current_frame: DivisionFrame
    ) -> List[Cell]:
        edited_cells: List[Cell] = []

        # The wall's Y coordinate is constant
        wall_y = current_frame.subregion_pos.y + current_frame.local_height - 1

        # Choose a random coordinate for the opening
        # We bound the coordinate from the beginning to the width - 2
        # For a slice of width 10, the opening will be between x=0 and x=8
        # Loop until we pick a non-locked cell
        # TODO: Use a set of available coordinates, removing from said set when we pick
        # This would avoid an infinite loop in there is no available cell
        opening_x = -1
        while (
            opening_x == -1
            or self.get_maze().map[wall_y][opening_x].locked
            or self.get_maze().map[wall_y + 1][opening_x].locked
        ):
            opening_x = self._get_rng().randint(
                current_frame.subregion_pos.x,
                current_frame.subregion_pos.x + current_frame.local_width - 2
            )

        # Loop through the wall's width
        for x in range(
            current_frame.subregion_pos.x,
            current_frame.subregion_pos.x + current_frame.local_width
        ):
            curr_cells = [
                self.get_maze().map[wall_y][x],
                self.get_maze().map[wall_y + 1][x]
            ]

            # Update the cells adjacent to the wall
            curr_cells[0].enclose(EDirection.SOUTH)
            curr_cells[1].enclose(EDirection.NORTH)
            edited_cells.extend(curr_cells)

        # Carve the cells with the opening
        self.get_maze().map[wall_y][opening_x].carve(EDirection.SOUTH)
        self.get_maze().map[wall_y][opening_x + 1].carve(EDirection.NORTH)
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
        tick_count: int = 0,
        seed: Optional[str] = None
    ) -> Union[
        List[List[Cell]],
        Generator[List[Cell], None, None],
    ]:
        # TODO: check the tick_count parameter and yield if it is > 0
        if seed is not None:
            self._get_rng().seed(seed)

        # Initialize the stack with a frame of the full maze
        stack: List[RecursiveDivisionGenerator.DivisionFrame] = [
            RecursiveDivisionGenerator.DivisionFrame(
                position=(
                    RecursiveDivisionGenerator.Position.TOP
                ),
                direction=(
                    RecursiveDivisionGenerator.Direction.HORIZONTAL
                    if self.get_maze().height > self.get_maze().width
                    else
                    RecursiveDivisionGenerator.Direction.VERTICAL
                ),
                local_height=self.get_maze().height,
                local_width=self.get_maze().width,
                subregion_pos=Vec2(0, 0)
            )
        ]

        updated_cells: List[Cell] = []
        while len(stack):
            # Get the frame to process
            current_frame = stack.pop()

            # Stop condition, the frame will be skipped if too small
            # TODO: keep slicing if one of the dimensions still allows it
            if max(
                current_frame.local_height,
                current_frame.local_width
            ) <= 2:
                continue

            # Slice 2 new frames
            new_frames: List[
                RecursiveDivisionGenerator.DivisionFrame
            ] = self.__create_new_frames(current_frame)

            # Add the wall for the current frame
            if (
                current_frame.position == RecursiveDivisionGenerator.Position.TOP
                or current_frame.position == RecursiveDivisionGenerator.Position.LEFT
            ):
                updated_cells.extend(
                    self.__add_wall(current_frame)
                )

            # Add the new frames to the stack
            stack.extend(new_frames)

        return updated_cells
