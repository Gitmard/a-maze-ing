# mazegen

A standalone Python maze generation library, built as part of the [a-maze-ing](https://github.com/smenard/a-maze-ing) project at 42 Lyon.

## Installation
```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

## Quick start
```python
from mazegen import DepthFirstSearchGenerator, MazeGenerator, Vec2, GeneratorException

generator: MazeGenerator = DepthFirstSearchGenerator(
    width=30,
    height=20,
    start_pos=Vec2(0, 0),
    end_pos=Vec2(29, 19),
)

generator.generate()
generator.get_maze().solve()

print(generator.get_solution())  # [(0,0), (1,0), ..., (29,19)]
```

## API Reference

### `DepthFirstSearchGenerator`

The only concrete generator provided by this package. Extends `MazeGenerator`.
```python
DepthFirstSearchGenerator(
    width: int,
    height: int,
    start_pos: Vec2,
    end_pos: Vec2,
    seed: str | None = None,        # RNG seed for reproducible generation
    add_ft_pattern: bool = False,   # Lock cells forming a "42" at the center
    is_perfect: bool = True,        # Enforce a single path between entry and exit
    output_file: str = "output_maze.txt",
)
```

#### Methods

| Method | Description |
|---|---|
| `generate()` | Run the DFS algorithm and populate the maze |
| `get_maze() -> Maze` | Return the underlying `Maze` object |
| `get_solution() -> list[Coord]` | Return the solution as a list of `(x, y)` tuples |
| `write_output_file()` | Serialize and write the maze to `output_file` |
| `reset_maze()` | Reset the maze to its blank state (useful before re-generating) |

---

### `Maze`

Represents the 2D grid. Obtained via `generator.get_maze()`.

| Attribute | Type | Description |
|---|---|---|
| `map` | `list[list[Cell]]` | Row-major grid of cells |
| `width` | `int` | Number of columns |
| `height` | `int` | Number of rows |
| `solution` | `list[Coord]` | Populated after `solve()` is called |
| `start_pos` | `Vec2` | Entry cell |
| `end_pos` | `Vec2` | Exit cell |

| Method | Description |
|---|---|
| `solve()` | Find the shortest path from entry to exit using A* |

---

### `Cell`

A single cell in the grid. Walls are stored as an `EDirection` bitmask — a set bit means the wall is present.

| Attribute | Type | Description |
|---|---|---|
| `position` | `Vec2` | Grid coordinates |
| `walls` | `int` | Current wall bitmask |
| `locked` | `bool` | Locked cells cannot be carved |

---

### `EDirection`

`IntFlag` enum representing the four cardinal directions. Can be combined with `|`.
```python
EDirection.NORTH  # 1 << 0
EDirection.EAST   # 1 << 1
EDirection.SOUTH  # 1 << 2
EDirection.WEST   # 1 << 3
EDirection.ALL    # 0b1111 — all walls present
```

---

### `Vec2`

Simple 2D integer coordinate dataclass.
```python
Vec2(x=0, y=0)
```

---

### `GeneratorException`

Raised on invalid operations during generation (carving a locked cell, out-of-bounds carve, invalid config, etc.).
```python
try:
    generator.generate()
except GeneratorException as e:
    print(e)  # GeneratorError: <message>
```

## Examples

### Reproducible generation with a seed
```python
generator = DepthFirstSearchGenerator(
    width=50,
    height=50,
    start_pos=Vec2(0, 0),
    end_pos=Vec2(49, 49),
    seed="my-seed",
)
generator.generate()
# Same seed → identical maze every time
```

### Accessing the grid
```python
generator.generate()
maze = generator.get_maze()

for row in maze.map:
    for cell in row:
        print(cell.position, bin(cell.walls))
```

### Checking if a wall is open in a given direction
```python
from mazegen import EDirection

cell = maze.map[3][5]

if not (cell.walls & EDirection.NORTH.value):
    print("North wall is open")
```

### Writing the output file
```python
generator.generate()
generator.get_maze().solve()
generator.write_output_file()  # writes to the path given at construction
```

### Re-generating without creating a new instance
```python
generator.reset_maze()
generator.generate()
generator.get_maze().solve()
```

## Output file format

Each cell is encoded as a single hex digit (0–F) representing its wall bitmask:

| Bit | Direction |
|-----|-----------|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 | West |

A set bit means the wall is **closed**. After the grid, a blank line separates three additional lines: entry coordinates, exit coordinates, and the solution path as a sequence of `N`/`E`/`S`/`W` characters.
```
FFFF...
...
FF9F...

0,0
29,19
EESSEENNE...
```

## Building from source
```bash
pip install build
python -m build
# Output: dist/mazegen-1.0.0-py3-none-any.whl
```