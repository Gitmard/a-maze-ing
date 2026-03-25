"""Maze visualizer using MLX graphical library.

Renders a maze with walls, entry/exit points, and an optional
solution path. Supports keyboard-driven color changes, path
toggling, and maze regeneration.
"""

import random
from enum import Enum
from typing import Any, Dict, List, Tuple, Union

from mlx import Mlx
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from generator import MazeGenerator
from generator.Cell import Cell
from generator.EDirection import EDirection

WALL_WIDTH_RATIO: float = 0.1


class EWalls(Enum):
    """Wall orientation variants."""

    HORIZONTAL = 0
    VERTICAL = 1


class EColorKeys(Enum):
    """Keys used to look up colours in the global palette."""

    WALLS = "walls"
    CELLS = "cells"
    ENTRY = "entry"
    EXIT = "exit"
    EMPTY = "empty"


class EEvents(Enum):
    """Event flags consumed by the main loop."""

    COLOR_CHANGE = "color_change"
    REGEN = "regen"
    PATH_TOGGLE = "path_toggle"
    QUIT = "quit"


Color = Tuple[int, int, int, int]
WallInfo = Tuple[Tuple[int, int], EWalls]


colors: Dict[EColorKeys, Color] = {
    EColorKeys.WALLS: (150, 150, 150, 255),
    EColorKeys.CELLS: (255, 255, 255, 255),
    EColorKeys.ENTRY: (255, 0, 150, 255),
    EColorKeys.EXIT: (200, 200, 0, 255),
    EColorKeys.EMPTY: (0, 0, 0, 255),
}


class Visualizer:
    """Render a maze into an MLX window.

    Args:
        generator: A ``MazeGenerator`` instance whose maze has
            already been initialised.
    """

    def __init__(self, generator: MazeGenerator) -> None:
        self.generator = generator
        self.maze: List[List[Cell]] = generator.get_maze().map
        self.maze_width: int = len(self.maze[0])
        self.maze_height: int = len(self.maze)

        self.m: Any = Mlx()
        self.mlx_ptr: Any = self.m.mlx_init()

        _, screen_width, screen_height = self.m.mlx_get_screen_size(
            self.mlx_ptr
        )

        screen_width = int(screen_width / 1.5)
        screen_height = int(screen_height / 1.5)
        screen_ratio: float = screen_width / screen_height
        maze_ratio: float = self.maze_width / self.maze_height

        if screen_ratio >= maze_ratio:
            self.window_height: int = screen_height
            self.window_width: int = int(screen_height * maze_ratio)
        else:
            self.window_width = screen_width
            self.window_height = int(screen_width / maze_ratio)

        self.cell_size: int = max(
            1,
            min(
                int(self.window_height / self.maze_height),
                int(self.window_width / self.maze_width),
            ),
        )

        self.wall_width: int = max(1, int(self.cell_size * WALL_WIDTH_RATIO))
        self.wall_height: int = self.cell_size + self.wall_width

        self.window_width = self.cell_size * self.maze_width + self.wall_width
        self.window_height = (
            self.cell_size * self.maze_height + self.wall_width
        )

        self.win_ptr: Any = self.m.mlx_new_window(
            self.mlx_ptr,
            self.window_width,
            self.window_height,
            "A-Maze-Ing",
        )
        self.isolated_cells: List[Cell] = [
            cell
            for row in self.maze
            for cell in row
            if cell.walls == EDirection.ALL
        ]

        self.img: Any = self.m.mlx_new_image(
            self.mlx_ptr, self.window_width, self.window_height
        )

        self.data: Any
        self.bpp: int
        self.line_len: int
        self.endian: int
        (
            self.data,
            self.bpp,
            self.line_len,
            self.endian,
        ) = self.m.mlx_get_data_addr(self.img)

        self.offset: int = int(self.wall_width / 2)
        self.needs_draw: bool = True

        self.entry: Any = self.generator.get_maze().start_pos
        self.exit: Any = self.generator.get_maze().end_pos

        self.path: List[Tuple[int, int]] = []
        self.need_to_draw_path: bool = False

    def fill_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Color,
    ) -> None:
        """Write a filled rectangle directly into the image buffer.

        Args:
            x: Left edge in pixels.
            y: Top edge in pixels.
            width: Rectangle width in pixels.
            height: Rectangle height in pixels.
            color: RGBA colour tuple.
        """
        bpp_bytes: int = self.bpp // 8
        pixel: bytes = bytes(color[:bpp_bytes])
        row: bytes = pixel * width

        for dy in range(height):
            py: int = y + dy
            if py < 0 or py >= self.window_height:
                continue

            start_x: int = max(x, 0)
            end_x: int = min(x + width, self.window_width)
            if start_x >= end_x:
                continue

            buf_offset: int = py * self.line_len + start_x * bpp_bytes
            clipped_len: int = (end_x - start_x) * bpp_bytes
            clipped_start: int = (start_x - x) * bpp_bytes

            self.data[buf_offset: buf_offset + clipped_len] = row[
                clipped_start: clipped_start + clipped_len
            ]

    def draw_isolated(self, color: Color) -> None:
        """Draw all locked (isolated) cells with the given colour.

        Args:
            color: RGBA colour tuple applied to every isolated cell.
        """
        for cell in self.isolated_cells:
            x: int = cell.position.x * self.cell_size
            y: int = cell.position.y * self.cell_size

            self.fill_rect(
                x + self.offset,
                y + self.offset,
                self.cell_size,
                self.cell_size,
                color,
            )

    def draw_path(self, draw_black: bool = False) -> None:
        """Draw the solution path with a gradient or erase it.

        When *draw_black* is ``False`` the path fades from the
        entry colour to the exit colour.  When ``True`` the path
        is overwritten with the empty colour.

        Args:
            draw_black: If ``True``, paint path cells black.
        """
        path_length: int = len(self.path)
        if path_length == 0:
            return

        entry_c: Color = colors[EColorKeys.ENTRY]
        exit_c: Color = colors[EColorKeys.EXIT]

        decay: Tuple[float, float, float, float] = (
            (exit_c[0] - entry_c[0]) / path_length,
            (exit_c[1] - entry_c[1]) / path_length,
            (exit_c[2] - entry_c[2]) / path_length,
            (exit_c[3] - entry_c[3]) / path_length,
        )

        for i, (cx, cy) in enumerate(self.path):
            color: Color
            if draw_black:
                color = colors[EColorKeys.EMPTY]
            else:
                color = (
                    int(entry_c[0] + decay[0] * i),
                    int(entry_c[1] + decay[1] * i),
                    int(entry_c[2] + decay[2] * i),
                    int(entry_c[3] + decay[3] * i),
                )

            px: int = cx * self.cell_size
            py: int = cy * self.cell_size

            self.fill_rect(
                px + self.offset,
                py + self.offset,
                self.cell_size,
                self.cell_size,
                color,
            )

    def draw_entry_exit(self) -> None:
        """Highlight the entry and exit cells."""
        ex: int = self.entry.x * self.cell_size
        ey: int = self.entry.y * self.cell_size

        self.fill_rect(
            ex + self.offset,
            ey + self.offset,
            self.cell_size,
            self.cell_size,
            colors[EColorKeys.ENTRY],
        )

        ox: int = self.exit.x * self.cell_size
        oy: int = self.exit.y * self.cell_size

        self.fill_rect(
            ox + self.offset,
            oy + self.offset,
            self.cell_size,
            self.cell_size,
            colors[EColorKeys.EXIT],
        )

    def draw_walls(self) -> None:
        """Render every wall segment for the entire maze."""
        decay: int = int(self.wall_width / 2)

        transformations: Dict[EDirection, WallInfo] = {
            EDirection.NORTH: (
                (-decay, -decay),
                EWalls.HORIZONTAL,
            ),
            EDirection.EAST: (
                (self.cell_size - decay, -decay),
                EWalls.VERTICAL,
            ),
            EDirection.SOUTH: (
                (-decay, self.cell_size - decay),
                EWalls.HORIZONTAL,
            ),
            EDirection.WEST: (
                (-decay, -decay),
                EWalls.VERTICAL,
            ),
        }

        directions: List[EDirection] = [
            EDirection.NORTH,
            EDirection.EAST,
            EDirection.SOUTH,
            EDirection.WEST,
        ]

        for row in self.maze:
            for cell in row:
                cx: int = cell.position.x * self.cell_size
                cy: int = cell.position.y * self.cell_size

                for direction in directions:
                    if not (cell.walls & direction.value):
                        continue

                    coord_tf, orientation = transformations[direction]
                    tx, ty = coord_tf
                    wx: int = cx + tx
                    wy: int = cy + ty

                    if orientation == EWalls.HORIZONTAL:
                        w: int = self.wall_height
                        h: int = self.wall_width
                    else:
                        w = self.wall_width
                        h = self.wall_height

                    self.fill_rect(
                        wx + self.offset,
                        wy + self.offset,
                        w,
                        h,
                        colors[EColorKeys.WALLS],
                    )

    def draw_empty(self) -> None:
        """Fill the entire image buffer with the empty colour."""
        self.fill_rect(
            0,
            0,
            self.window_width,
            self.window_height,
            colors[EColorKeys.EMPTY],
        )

    def draw_maze(self) -> None:
        """Composite all maze layers and flush to the window."""
        self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_IMAGE_WRITABLE, self.img)

        if self.need_to_draw_path:
            self.draw_path()
        else:
            self.draw_path(draw_black=True)

        self.draw_isolated(colors[EColorKeys.CELLS])
        self.draw_entry_exit()
        self.draw_walls()

        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img, 0, 0
        )
        self.m.mlx_sync(self.mlx_ptr, self.m.SYNC_WIN_FLUSH, self.win_ptr)

    def run_visualizer(self, state: Dict[EEvents, bool]) -> None:
        """Enter the MLX event loop, reacting to *state* flags.

        Args:
            state: Mutable dictionary whose boolean flags are set
                by the keyboard listener and consumed each frame.
        """

        def on_loop(_: Any) -> None:
            if state[EEvents.REGEN]:
                self.draw_empty()
                self.generator.generate()
                self.maze = self.generator.get_maze().map
                self.isolated_cells = [
                    cell
                    for row in self.maze
                    for cell in row
                    if cell.walls == EDirection.ALL
                ]
                self.generator.get_maze().solve()
                self.path = self.generator.get_maze().solution
                self.draw_maze()
                state[EEvents.REGEN] = False

            if state[EEvents.PATH_TOGGLE]:
                self.need_to_draw_path = not self.need_to_draw_path
                self.draw_maze()
                state[EEvents.PATH_TOGGLE] = False

            if state[EEvents.COLOR_CHANGE]:
                colors[EColorKeys.WALLS] = (
                    random.randint(75, 200),
                    random.randint(75, 200),
                    random.randint(75, 200),
                    255,
                )
                self.draw_maze()
                state[EEvents.COLOR_CHANGE] = False

            if state[EEvents.QUIT]:
                self.m.mlx_loop_exit(self.mlx_ptr)

        def on_close(_: Any) -> None:
            self.m.mlx_loop_exit(self.mlx_ptr)

        self.m.mlx_loop_hook(self.mlx_ptr, on_loop, None)
        self.m.mlx_hook(self.win_ptr, 33, 0, on_close, None)
        self.m.mlx_loop(self.mlx_ptr)

    def destroy_ptr(self) -> None:
        """Release all MLX resources (image, window, context)."""
        self.m.mlx_destroy_image(self.mlx_ptr, self.img)
        self.m.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.m.mlx_release(self.mlx_ptr)


def visualize(generator: MazeGenerator) -> None:
    """Create a visualiser window and run until closed.

    Keyboard controls:
        * **c** - randomise wall colour
        * **p** - toggle solution path
        * **r** - regenerate maze
        * **q** - quit

    Args:
        generator: The maze generator to visualise.
    """
    state: Dict[EEvents, bool] = {
        EEvents.COLOR_CHANGE: False,
        EEvents.PATH_TOGGLE: False,
        EEvents.REGEN: True,
        EEvents.QUIT: False,
    }

    def on_press(
        key: Union[Key, KeyCode, None],
    ) -> None:
        if not isinstance(key, KeyCode):
            return
        if key.char is None:
            return

        match key.char:
            case "c":
                state[EEvents.COLOR_CHANGE] = True
            case "p":
                state[EEvents.PATH_TOGGLE] = True
            case "r":
                state[EEvents.REGEN] = True
            case "q":
                state[EEvents.QUIT] = True

    visualizer = Visualizer(generator)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    visualizer.run_visualizer(state)
    visualizer.destroy_ptr()

    listener.stop()
