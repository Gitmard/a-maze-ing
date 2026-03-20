import mlx

from typing import List, Tuple

from dataclasses import dataclass

import time

import random


colors = {
    "walls": (150, 150, 150, 255),
    "cells": (255, 255, 255, 255)
}


WALL_WIDTH_RATIO = 0.1


@dataclass
class Vec2:
    x: int
    y: int


class Cell:
    def __init__(self, position: Vec2, walls: int, is_isolated: bool):
        self.position = position
        self.walls = walls
        self.is_isolated = is_isolated


def parse_maze(file_path: str) -> List[List[Cell]]:
    maze: List[List[Cell]] = []
    with open(file_path, 'r') as f:
        for y, line in enumerate(f):
            line = line.strip()
            if not line:
                break
            row: List[Cell] = []
            for x, ch in enumerate(line):
                walls = int(ch, 16)
                is_isolated = walls == 0xF
                row.append(Cell(Vec2(x, y), walls, is_isolated))
            maze.append(row)
    return maze


class Visualizer:
    def __init__(self, maze: List[List[Cell]]):
        self.maze = maze
        self.maze_width = len(maze[0])
        self.maze_height = len(maze)

        self.m = mlx.Mlx()
        self.mlx_ptr = self.m.mlx_init()

        _, screen_width, screen_height = self.m.mlx_get_screen_size(
            self.mlx_ptr
        )

        screen_width = int(screen_width / 1.5)
        screen_height = int(screen_height / 1.5)
        screen_ratio = screen_width / screen_height
        maze_ratio = self.maze_width / self.maze_height

        if screen_ratio >= maze_ratio:
            self.window_height = screen_height
            self.window_width = int(screen_height * maze_ratio)
        else:
            self.window_width = screen_width
            self.window_height = int(screen_width / maze_ratio)

        self.cell_size = max(
            1,
            min(
                int(self.window_height / self.maze_height),
                int(self.window_width / self.maze_width)
            )
        )

        self.wall_width = max(1, int(self.cell_size * WALL_WIDTH_RATIO))
        self.wall_height = self.cell_size + self.wall_width

        self.window_width = self.cell_size * self.maze_width \
            + self.wall_width
        self.window_height = self.cell_size * self.maze_height \
            + self.wall_width

        self.win_ptr = self.m.mlx_new_window(
            self.mlx_ptr,
            self.window_width,
            self.window_height,
            "A-Maze-Ing"
        )

        self.isolated_cells = [
            cell for row in self.maze
            for cell in row
            if cell.is_isolated is True
        ]

        self.v_wall = self.m.mlx_new_image(
            self.mlx_ptr, self.wall_width, self.wall_height
        )
        self.colorate_image(self.v_wall, colors["walls"])

        self.h_wall = self.m.mlx_new_image(
            self.mlx_ptr, self.wall_height, self.wall_width
        )
        self.colorate_image(self.h_wall, colors["walls"])

        self.cell = self.m.mlx_new_image(
            self.mlx_ptr, self.cell_size, self.cell_size
        )
        self.colorate_image(self.cell, colors["cells"])

        self.img = self.m.mlx_new_image(
            self.mlx_ptr, self.window_width, self.window_height
        )

        self.data, self.bpp, self.line_len, self.endian = \
            self.m.mlx_get_data_addr(self.img)

        self.offset = int(self.wall_width / 2)

        self.needs_draw = True

    def fill_rect(self, x, y, width, height, color):
        bpp_bytes = self.bpp // 8
        pixel = bytes(color[:bpp_bytes])
        row = pixel * width

        for dy in range(height):
            py = y + dy
            if py < 0 or py >= self.window_height:
                continue

            start_x = max(x, 0)
            end_x = min(x + width, self.window_width)
            if start_x >= end_x:
                continue

            offset = py * self.line_len + start_x * bpp_bytes
            clipped_len = (end_x - start_x) * bpp_bytes
            clipped_start = (start_x - x) * bpp_bytes

            self.data[offset:offset + clipped_len] = \
                row[clipped_start:clipped_start + clipped_len]

    def colorate_image(self, image, color: Tuple[int, int, int, int]):
        data, _, _, _ = self.m.mlx_get_data_addr(image)

        for i in range(0, len(data), 4):
            for j in range(len(color)):
                data[i + j] = color[j]

    def draw_isolated(self, color):
        for cell in self.isolated_cells:
            x = cell.position.x * self.cell_size
            y = cell.position.y * self.cell_size

            self.fill_rect(
                x + self.offset,
                y + self.offset,
                self.cell_size,
                self.cell_size,
                color
            )

    def draw_walls(self, color):

        decay = int(self.wall_width / 2)
        transformtions = {
            0: ((-decay, -decay),
                self.h_wall),

            1: ((self.cell_size - decay, -decay),
                self.v_wall),

            2: ((-decay, self.cell_size - decay),
                self.h_wall),

            3: ((-decay, -decay),
                self.v_wall),
        }

        for row in self.maze:
            for cell in row:
                x = cell.position.x * self.cell_size
                y = cell.position.y * self.cell_size

                for shift in range(4):
                    if cell.walls & (1 << shift):
                        coord_transform, image = transformtions[shift]
                        transform_x, transform_y = coord_transform

                        now_x = x + transform_x
                        now_y = y + transform_y

                        if image == self.h_wall:
                            height = self.wall_width
                            width = self.wall_height
                        else:
                            height = self.wall_height
                            width = self.wall_width

                        self.fill_rect(
                            now_x + self.offset,
                            now_y + self.offset,
                            width,
                            height,
                            color
                        )

    def draw_maze(self):

        self.m.mlx_sync(
            self.mlx_ptr, self.m.SYNC_IMAGE_WRITABLE, self.img
        )

        self.draw_isolated(colors["cells"])
        self.draw_walls(colors["walls"])

        self.m.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_ptr,
            self.img,
            0,
            0
        )

        self.m.mlx_sync(
            self.mlx_ptr, self.m.SYNC_WIN_FLUSH, self.win_ptr
        )

    def run_visualizer(self):

        last_draw = time.time()

        def on_loop(_):
            nonlocal last_draw

            if self.needs_draw:
                self.draw_maze()
                self.needs_draw = False

            colors["walls"] = (
                random.randint(50, 150),
                random.randint(50, 150),
                random.randint(50, 150),
                255
            )
            time.sleep(0.01)
            self.draw_maze()

        def on_close(_):
            self.m.mlx_loop_exit(self.mlx_ptr)

        self.m.mlx_loop_hook(self.mlx_ptr, on_loop, None)
        self.m.mlx_hook(self.win_ptr, 33, 0, on_close, None)

        self.m.mlx_loop(self.mlx_ptr)

    def destrory_ptr(self):
        self.m.mlx_destroy_image(self.mlx_ptr, self.cell)
        self.m.mlx_destroy_image(self.mlx_ptr, self.v_wall)
        self.m.mlx_destroy_image(self.mlx_ptr, self.h_wall)
        self.m.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.m.mlx_release(self.mlx_ptr)


maze = parse_maze("maze.txt")
visualizer = Visualizer(maze)

visualizer.run_visualizer()
visualizer.destrory_ptr()
