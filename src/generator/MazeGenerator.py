from generator.GeneratorException import GeneratorException
from generator.Vec2 import Vec2
from generator.Cell import Cell
from generator.Maze import Coord, Maze
from typing import Optional, Union, List
from abc import ABC, abstractmethod
from random import Random


class MazeGenerator(ABC):

    __maze: Maze
    __seed: Union[str, None]
    __rng: Random
    __height: int
    __width: int
    __start_pos: Vec2
    __end_pos: Vec2
    __add_ft_pattern: bool
    __output_file: str

    def __init__(
        self,
        width: int,
        height: int,
        start_pos: Vec2,
        end_pos: Vec2,
        seed: Optional[str] = None,
        add_ft_pattern: bool = False,
        is_perfect: bool = True,
        output_file: str = "output_maze.txt",
    ) -> None:
        self.__seed = seed
        self.__rng = Random(seed)
        self.__maze = Maze()
        self.__width = width
        self.__height = height
        self.__start_pos = start_pos
        self.__end_pos = end_pos
        self.__add_ft_pattern = add_ft_pattern
        self.__maze.init_map(width, height, start_pos, end_pos, add_ft_pattern)
        self.__is_perfect = is_perfect
        self.__output_file = output_file

    @abstractmethod
    def generate(self, seed: Optional[str] = None) -> List[Cell]:
        pass

    def reset_maze(self) -> None:
        self.__maze.reset_map()
        self.__maze.init_map(
            self.__width,
            self.__height,
            self.__start_pos,
            self.__end_pos,
            self.__add_ft_pattern,
        )

    def find_shortest_path(self) -> List[Cell]:
        # TODO: Implement A* algorithm
        raise NotImplementedError(
            "Method find_shortest_path of MazeGenerator"
            + " not yet implemented"
        )

    def __format_output(self) -> str:
        digits = "0123456789ABCDEF"
        output = ""
        for line in self.get_maze().map:
            for cell in line:
                if cell.walls > len(digits):
                    raise GeneratorException(
                        f"Invalid walls value {cell.walls}"
                    )
                digit = digits[cell.walls]
                output += digit
            output += "\n"
        output += "\n"
        output += f"{self.__start_pos.x,self.__start_pos.y}\n"
        output += f"{self.__end_pos.x,self.__end_pos.y}\n"
        solution_coords = [(0, 0)] + self.get_solution()
        solutions_moves = ""
        for i in range(len(solution_coords) - 1):
            curr_coords = solution_coords[i]
            next_coords = solution_coords[i + 1]
            if curr_coords[0] < next_coords[0]:
                solutions_moves += "E"
            elif curr_coords[0] > next_coords[0]:
                solutions_moves += "W"
            elif curr_coords[1] < next_coords[1]:
                solutions_moves += "S"
            elif curr_coords[1] > next_coords[1]:
                solutions_moves += "N"
        output += solutions_moves
        output += "\n"
        return output

    def write_output_file(self) -> None:
        with open(self.__output_file, "w") as out:
            out.write(self.__format_output())

    def get_solution(self) -> List[Coord]:
        return self.__maze.solution

    def get_maze(self) -> Maze:
        return self.__maze

    def _get_seed(self) -> Union[str, None]:
        return self.__seed

    def _get_rng(self) -> Random:
        return self.__rng

    def _get_perfect(self) -> bool:
        return self.__is_perfect
