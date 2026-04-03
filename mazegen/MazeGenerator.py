from mazegen.GeneratorException import GeneratorException
from mazegen.Vec2 import Vec2
from mazegen.Cell import Cell
from mazegen.Maze import Coord, Maze
from typing import Literal, Optional, Union, List
from abc import ABC, abstractmethod
from random import Random
from config_validation import ConfigValidator


class MazeGenerator(ABC):
    """
    Abstract base class for maze generators.

    Handles maze initialization, output formatting, and file writing.
    Subclasses must implement the `generate` method with their own algorithm.
    """

    __maze: Maze
    __seed: Union[str, None]
    __rng: Random
    __height: int
    __width: int
    __start_pos: Vec2
    __end_pos: Vec2
    __output_file: str
    __locked_cells: Optional[List[List[Literal[0, 1]]]]

    def __init__(
        self,
        width: int,
        height: int,
        start_pos: Vec2,
        end_pos: Vec2,
        seed: Optional[str] = None,
        locked_cells: Optional[List[List[Literal[0, 1]]]] = None,
        is_perfect: bool = True,
        output_file: str = "output_maze.txt",
    ) -> None:
        """
        Initialize the maze generator and its underlying maze structure.

        Args:
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            start_pos: Entry point of the maze.
            end_pos: Exit point of the maze.
            seed: Optional RNG seed for reproducible generation.
            add_ft_pattern: Whether to overlay the 42 pattern onto the maze.
            is_perfect: Whether the maze should be perfect.
            output_file: Path to the file where the maze will be written.
        """
        ConfigValidator.validate(
            height=height,
            width=width,
            entry=start_pos,
            exit=end_pos,
            seed=seed,
            perfect=is_perfect,
            output_file=output_file
        )
        self.__seed = seed
        self.__rng = Random(seed)
        self.__maze = Maze()
        self.__width = width
        self.__height = height
        self.__start_pos = start_pos
        self.__end_pos = end_pos
        self.__locked_cells = locked_cells
        self.__maze.init_map(width, height, start_pos, end_pos, locked_cells)
        self.__is_perfect = is_perfect
        self.__output_file = output_file

    @abstractmethod
    def generate(self, seed: Optional[str] = None) -> List[Cell]:
        """
        Run the maze generation algorithm.

        Args:
            seed: Optional seed to override the one set at construction.

        Returns:
            The list of cells in the order they were visited during generation.
        """
        pass

    def reset_maze(self) -> None:
        """Reset the maze to its initial state, clearing all generated walls
        and paths."""
        self.__maze.reset_map()
        self.__maze.init_map(
            self.__width,
            self.__height,
            self.__start_pos,
            self.__end_pos,
            self.__locked_cells,
        )

    def __format_output(self) -> str:
        """
        Serialize the maze into the expected output format.

        Each cell's wall bitmask is encoded as a single hex digit (0-F).
        The output contains the maze grid, start/end coordinates,
        and the solution as a sequence of cardinal direction characters
        (N/S/E/W).

        Returns:
            The formatted maze string ready to be written to a file.

        Raises:
            GeneratorException: If a cell's wall value exceeds the encodable
            range (> 15).
        """
        digits = "0123456789ABCDEF"
        output = ""
        for line in self.get_maze().map:
            for cell in line:
                if cell.walls >= len(digits):
                    raise GeneratorException(
                        f"Invalid walls value {cell.walls}"
                    )
                digit = digits[cell.walls]
                output += digit
            output += "\n"
        output += "\n"
        output += f"{self.__start_pos.x},{self.__start_pos.y}\n"
        output += f"{self.__end_pos.x},{self.__end_pos.y}\n"
        solution_coords = [(self.__start_pos.x, self.__start_pos.y)] + \
            self.get_solution()
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
        """Format and write the maze to the configured output file."""
        with open(self.__output_file, "w") as out:
            out.write(self.__format_output())

    def get_solution(self) -> List[Coord]:
        """Return the solution path as a list of (x, y) coordinates."""
        return self.__maze.solution

    def get_maze(self) -> Maze:
        """Return the underlying Maze instance."""
        return self.__maze

    def _get_seed(self) -> Union[str, None]:
        """Return the seed used for RNG, or None if unseeded."""
        return self.__seed

    def _get_rng(self) -> Random:
        """Return the RNG instance used by this generator."""
        return self.__rng

    def _get_perfect(self) -> bool:
        """Return whether this generator is configured
        to produce a perfect maze."""
        return self.__is_perfect
