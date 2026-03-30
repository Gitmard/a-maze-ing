from mazegen.GeneratorException import GeneratorException
from mazegen.EDirection import EDirection
from mazegen.Vec2 import Vec2


class Cell:
    """A single cell in the maze grid.

    Walls are stored as an ``EDirection`` bitmask: a set bit means the wall
    is present, a cleared bit means it has been carved open.

    Attributes:
        position: Grid coordinates of this cell.
        walls: Bitmask of current walls. Defaults to ``EDirection.ALL``
        (fully enclosed).
        locked: If ``True``, the cell cannot be carved or modified
        by the generator.
    """

    position: Vec2
    locked: bool
    walls: int

    def __init__(
        self,
        position: Vec2,
        walls: int = EDirection.ALL.value,
        locked: bool = False,
    ):
        """
        Args:
            position: Grid coordinates of this cell.
            walls: Initial wall bitmask. Defaults to all walls present.
            locked: Whether the cell is locked against modification.
        """
        self.position = position
        self.walls = walls
        self.locked = locked

    def carve(self, direction: EDirection) -> None:
        """Remove a wall in the given direction (clear its bit).

        No-op if the wall is already absent.

        Args:
            direction: The wall to remove.

        Raises:
            GeneratorException: If the cell is locked.
        """
        if self.locked:
            raise GeneratorException("Cannot edit a locked cell")
        if self.walls & direction.value:
            self.walls -= direction.value

    def reset_cell(self) -> None:
        """Restore all walls and unlock the cell."""
        self.walls = EDirection.ALL.value
        self.locked = False
