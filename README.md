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

## Config File

## Alogrithms

## Reusability

## Project Managemement

### Roles

### Planning

### Critical Retrospective