from enum import IntFlag


class EDirection(IntFlag):
    NORTH = 1 << 0
    EAST = 1 << 1
    SOUTH = 1 << 2
    WEST = 1 << 3
    ALL = 15
