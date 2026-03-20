from abc import ABC, abstractmethod
from .Cell import Cell
from .Maze import Maze
from typing import Union, List, Generator, Any


class MazeGenerator(ABC):
    __solution: Union[List[Cell], None]
    __maze: Maze

    @abstractmethod
    def generate(self, tick_count: int = -1) -> Union[
        List[List[Any]],
        Generator[List[Any], None, None]
    ]:
        pass

    def reset_maze(self) -> None:
        self.__maze.reset_map()

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

    def get_maze(self) -> Any:
        return self.__maze
