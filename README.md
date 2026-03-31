*This project has been created as part of the 42 curriculum by smenard, vquetier.*

# a-maze-ing
> This is the way

## Description

A-maze-ing is part of the common core curriculum. It's goal is to provide an introduction to graphical programming and maze generation algorithms

The maze generation part of this project is ment to be reusable and to serve in a later project, PacMan, during wich the students will have to create a clone of the classic arcade game

## Instructions

This project uses a virtual environment and a Makefile to streamline dependency management

To setup the venv and install the dependencies, use `make install`

To run the project, use `make run`

To lint the source code, use `make lint` or `make lint-strict`

To remove the `__pycache__` and `.mypy_cache`, use `make clean`

You can also delete the virtual environment files with `make fclean`

Finally, use `make debug` to run a-maze-ing with pdb, python's builtin debugger

When ran, a-maze-ing will read from the config file given as an argument to generate a maze. See the section *Config File* for details on the required structure.

Once the maze generation is done, a visualizer will show the result.

### Visualizer controls

| Keybind | Action                                            |
|---------|---------------------------------------------------|
| r       | Generate a new maze                               |
| c       | Change the colors of the walls                    |
| p       | Show the shortest path from the entry to the exit |
| q       | Close the program                                 |


## Resources

Chepa drr

## Config File

A-maze-ing uses a config file to declare the dimension of the maze, the positions of the entry and the exit, the name of the output file, if the generated maze sould be *perfect* (only one path from the entry to the exit) and the seed used by the random number generator.

Here is an example of a config file:
```
WIDTH=100
HEIGHT=100
ENTRY=0,0
EXIT=99,99
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=amazing!
```

This config file can have any name, by default, the Makefile gives `config.txt` to the project but you can override the name with `make run [jsp frr mais on peut c'est sûr]`

## Alogrithms

Our maze generator uses the Depth-First-Search algorithm.

### Behaviour

Depth first search uses a set of visited cells and a stack of the current path taken to generate perfect mazes.

For DFS, the maze needs to be initialized with every cell fully enclosed.

We intilialize the stack with an arbitrary cell (the one at 0,0 in our implementation). We then pick a random direction and remove the wall between the 2 cells, push the new cell to the stack and to to visited set. We repeat this process until there is no available direction then we backtrack (pop the last cell in the stack) until we find ourself at a position where we have an available direction.

A-maze-ing as a little quirk, every maze (when the size allows it) must have obstacles that trace a 42 in the middle of the maze. DFS allows us to work around the obstacles very elegently, when we pick a random direction to continue, we can exclude the ones that will lead to a locked cell (part of the 42)

Since we never visit the same cell twice (thanks to the visited cells set), we are guaranteed to get a perfect maze out of this algorithm.

## Reusability

The maze generator of a-maze-ing must be reusable in other projects. Our project builds a standalone .whl archive that will include the source code of the generator module that can then be imported in any python project.

### Example use:

```python
from mazegen import MazeGenerator # Abstract class for polymorphism
from mazegen import DepthFirstSearchGenerator # Specific DFS implementation
from mazegen import Vec2 # Data class used to represent 2D coordinates

generator: MazeGenerator = DepthFirstSearchGenerator(
            width=30,
            height=20,
            entry=Vec2(0, 0),
            exit=Vec2(29, 19),
            seed="my-seed",
            output_file="maze_output.txt",
            is_perfect=True,
            locked_cells=[
                [1, 0, 0, 0, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 0, 1, 1, 1],
                [0, 0, 1, 0, 1, 0, 0],
                [0, 0, 1, 0, 1, 1, 1],
            ] # Optionnal locked cells (for the 42 pattern in this case).
			  # This argument defaults to None. If you only want a maze without obstacles, leave this argument to its default value.
        )

generator.generate() # Run the DepthFirstSearch algorithm

generator.get_maze().solve() # Compute the shortest path between entry and exit using the A* algorithm

generator.write_output_file() # Write an output file with the maze, entry and exit points and the shortest path to the file given to the constructor
```

### Generator module structure



## Project Managemement

### Roles

### Planning

### Critical Retrospective