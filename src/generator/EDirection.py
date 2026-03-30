from enum import IntFlag


class EDirection(IntFlag):
    """Bitmask flags representing the four cardinal directions.

    Built on ``IntFlag``, values can be combined with bitwise operators
    to express multiple directions at once (e.g. ``NORTH | EAST``).
    """

    NORTH = 1 << 0
    EAST = 1 << 1
    SOUTH = 1 << 2
    WEST = 1 << 3
    ALL = 15  # NORTH | EAST | SOUTH | WEST
