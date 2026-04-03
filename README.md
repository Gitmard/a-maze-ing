*This project has been created as part of the 42 curriculum by smenard, vquetier.*

# a-maze-ing
> This is the way

## Description

A-maze-ing is part of the common core curriculum. Its goal is to provide an introduction to graphical programming and maze generation algorithms.

The program reads a configuration file, generates a maze, displays it visually in the terminal, and writes the result to an output file. The maze generation logic is packaged as a standalone, reusable Python module (`mazegen`) intended to be reused in a later project — PacMan — where students will build a clone of the classic arcade game.

## Instructions

This project uses a virtual environment and a Makefile to streamline dependency management.

| Command | Description |
|---|---|
| `make install` | Set up the venv and install dependencies |
| `make run` | Run the project with the default `config.txt` |
| `make run CONFIG=myfile.txt` | Run with a custom config file |
| `make lint` | Run `flake8` and `mypy` |
| `make lint-strict` | Run `mypy --strict` |
| `make debug` | Run with Python's built-in debugger (`pdb`) |
| `make clean` | Remove `__pycache__` and `.mypy_cache` |
| `make fclean` | Remove the virtual environment files |

### Visualizer controls

| Key | Action |
|-----|--------|
| `r` | Generate a new maze |
| `c` | Cycle through wall color themes |
| `p` | Toggle shortest path display |
| `q` | Quit |

## Config File

The config file uses `KEY=VALUE` pairs, one per line. Lines starting with `#` are treated as comments and ignored.

| Key | Description | Example |
|---|---|---|
| `WIDTH` | Number of columns | `WIDTH=100` |
| `HEIGHT` | Number of rows | `HEIGHT=100` |
| `ENTRY` | Entry cell coordinates | `ENTRY=0,0` |
| `EXIT` | Exit cell coordinates | `EXIT=99,99` |
| `OUTPUT_FILE` | Path of the output file | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Enforce a single path between entry and exit | `PERFECT=True` |
| `SEED` | RNG seed for reproducible generation (optional) | `SEED=amazing!` |

A default `config.txt` is provided at the root of the repository.

## Algorithm

Our maze generator uses **Depth-First Search (DFS)** with a stack and a visited set.

### How it works

The maze is initialized with every cell fully enclosed (all 4 walls present). DFS starts from cell `(0, 0)`, picks a random unvisited neighbour, carves the wall between them, and pushes the new cell onto the stack. When no unvisited neighbour is available, it backtracks by popping the stack until one is found. The process repeats until every reachable cell has been visited.

### Why DFS

DFS was chosen because it handles **locked-cell obstacles** (the 42 pattern) naturally: when picking a direction to expand, locked cells are simply excluded from the candidates. The algorithm routes around them without any special casing. This is a key requirement of the project.

We originally attempted to use Recursive Division, but that algorithm builds walls top-down rather than carving passages — making it fundamentally incompatible with pre-locked cells. Switching to DFS resolved this entirely.

## Reusability

The maze generation logic is packaged as a standalone Python module: `mazegen`. It is distributed as a `.whl` archive located at the root of the repository, installable via `pip`.

### Package structure

```
mazegen
├── Cell.py                     # Maze cell with bitmask wall representation
├── DepthFirstSearchGenerator.py # DFS algorithm implementation
├── EDirection.py               # Cardinal directions as IntFlag bitmask
├── GeneratorException.py       # Custom exception
├── MazeGenerator.py            # Abstract base class
├── Maze.py                     # 2D grid + A* solver
└── Vec2.py                     # 2D integer coordinate dataclass
```

### Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Building the package

```bash
pip install build
python -m build
```

### Usage example

```python
from mazegen import DepthFirstSearchGenerator, MazeGenerator, Vec2, GeneratorException

generator = DepthFirstSearchGenerator(
	width=30,
	height=20,
	start_pos=Vec2(0, 0),
	end_pos=Vec2(29, 19),
	seed="my_seed!!",
	output_file="output_maze.txt",
	is_perfect=True,
	locked_cells=[
		[1, 0, 0, 0, 1, 1, 1],
		[1, 0, 0, 0, 0, 0, 1],
		[1, 1, 1, 0, 1, 1, 1],
		[0, 0, 1, 0, 1, 0, 0],
		[0, 0, 1, 0, 1, 1, 1],
	]  # Optional: Add obstacles in the maze
)

try:
    generator.generate()               # Run the DFS algorithm
    generator.get_maze().solve()       # Compute the shortest path with A*
    generator.write_output_file()      # Write the output file

    maze = generator.get_maze()        # Access the Maze object
    solution = generator.get_solution()  # List of (x, y) coords from entry to exit
except GeneratorException as e:
    print("Generation failed:", e)
```

## Resources

No external resources were used for this project — we already knew the DFS algorithm and implemented it from scratch.

### Reference material

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Depth-first search — Wikipedia](https://en.wikipedia.org/wiki/Depth-first_search)
- [A* search algorithm — Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)

### AI use

AI tools were used in the following ways:
- **GitHub Copilot** — pull request reviews throughout the project
- **Claude (Anthropic)** — development aid: architecture discussion, debugging, and docstring writing

No AI-generated code was submitted as part of this project.

## Project Management

### Roles

| Login | Responsibilities |
|---|---|
| `smenard` | Maze generator module, README |
| `vquetier` | Makefile, config parsing, visualizer |

### Planning

We started the project aiming to implement Recursive Division. After significant development work, we discovered it is incompatible with pre-locked obstacle cells — the algorithm assumes a fully open grid to subdivide. We pivoted to DFS, which solved the problem cleanly.

### Retrospective

**What went well:** DFS turned out to be a better fit than expected. Its elegance with locked cells meant very little extra logic was needed to support the 42 pattern. The separation between the `mazegen` module and the visualizer also paid off — each part could be developed and tested independently.

**What could be improved:** A more thorough planning phase would have prevented the algorithm switch. Evaluating algorithm constraints against project requirements before writing any code is the main lesson taken from this project.
