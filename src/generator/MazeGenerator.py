from abc import ABC, abstractmethod
from random import Random
from .Cell import Cell
from .Maze import Maze
from typing import Optional, Union, List, Any


class MazeGenerator(ABC):
    __solution: Union[List[Cell], None]
    __maze: Maze
    __seed: Union[str, None]
    __rng: Random
    __height: int
    __width: int

    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[str] = None
    ) -> None:
        self.__seed = seed
        self.__rng = Random(seed)
        self.__maze = Maze()
        self.__width = width
        self.__height = height
        self.__maze.init_map(width, height)

    @abstractmethod
    def generate(
        self,
        seed: Optional[str] = None
    ) -> List[List[Any]]:
        pass

    def reset_maze(self) -> None:
        self.__maze.reset_map()
        self.__maze.init_map(self.__width, self.__height)

    def find_shortest_path(self) -> List[Cell]:
        # TODO: Implement A* algorithm
        raise NotImplementedError(
            "Method find_shortest_path of MazeGenerator"
            + " not yet implemented"
        )

    def format_output(self) -> str:
        # TODO: Format the maze to an output string
        raise NotImplementedError(
            "Method format_output of MazeGenerator"
            + " not yet implemented"
        )

    def get_solution(self) -> Union[List[Cell], None]:
        return self.__solution

    def get_maze(self) -> Maze:
        return self.__maze

    def _get_seed(self) -> Union[str, None]:
        return self.__seed

    def _get_rng(self) -> Random:
        return self.__rng
