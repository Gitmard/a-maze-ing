from dataclasses import dataclass


@dataclass
class Vec2:
    """A 2D integer coordinate pair.

    Attributes:
        x: Horizontal component.
        y: Vertical component.
    """

    x: int
    y: int
