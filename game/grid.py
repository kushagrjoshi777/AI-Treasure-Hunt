"""
Grid class for the AI Treasure Hunt game.

The grid is a 2-D rectangular world whose cells are either open (walkable) or
walls.  It stores the start position and the treasure (goal) position and
exposes the neighbour-query interface consumed by the search algorithms.
"""


class Grid:
    """
    Represents the grid world with walls, start, and treasure positions.

    Coordinates are (row, col) tuples with (0, 0) at the top-left corner.

    Parameters
    ----------
    rows : int
        Number of rows in the grid.
    cols : int
        Number of columns in the grid.
    walls : iterable of (row, col), optional
        Initial set of wall positions.  Defaults to an empty set.
    start : (row, col), optional
        Starting position for all agents.  Defaults to (rows-2, 1) — near the
        bottom-left, avoiding the border.
    treasure : (row, col), optional
        Goal position.  Defaults to (1, cols-2) — near the top-right.
    """

    def __init__(self, rows: int, cols: int,
                 walls=None, start=None, treasure=None):
        self.rows     = rows
        self.cols     = cols
        self.walls    = set(walls) if walls else set()
        self.start    = start    or (rows - 2, 1)
        self.treasure = treasure or (1, cols - 2)

    # ── Neighbour query (used by all search algorithms) ───────────────────────

    def get_neighbors(self, pos: tuple) -> list:
        """
        Return the 4-directional (N, S, W, E) neighbours of *pos* that are
        within the grid boundary and not walls.

        Parameters
        ----------
        pos : (row, col)

        Returns
        -------
        list of (row, col)
        """
        r, c       = pos
        neighbors  = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < self.rows
                    and 0 <= nc < self.cols
                    and (nr, nc) not in self.walls):
                neighbors.append((nr, nc))
        return neighbors

    # ── Validity / wall helpers ───────────────────────────────────────────────

    def is_valid(self, pos: tuple) -> bool:
        """Return True if *pos* is inside the grid and not a wall."""
        r, c = pos
        return (0 <= r < self.rows
                and 0 <= c < self.cols
                and pos not in self.walls)

    def is_wall(self, pos: tuple) -> bool:
        """Return True if *pos* is a wall cell."""
        return pos in self.walls

    def set_wall(self, pos: tuple) -> None:
        """
        Mark *pos* as a wall.

        The start and treasure cells are protected — they can never become
        walls so that the grid always has a valid start/goal.
        """
        if pos != self.start and pos != self.treasure:
            self.walls.add(pos)

    def remove_wall(self, pos: tuple) -> None:
        """Remove the wall at *pos* (no-op if it was not a wall)."""
        self.walls.discard(pos)

    def toggle_wall(self, pos: tuple) -> None:
        """
        Toggle the wall state of *pos*.

        If it is currently a wall it becomes open; if open it becomes a wall
        (subject to the same start/treasure protection as :meth:`set_wall`).
        """
        if pos in self.walls:
            self.remove_wall(pos)
        else:
            self.set_wall(pos)

    # ── Grid duplication ─────────────────────────────────────────────────────

    def copy(self) -> 'Grid':
        """Return a deep copy of this grid (walls set is duplicated)."""
        return Grid(self.rows, self.cols,
                    set(self.walls), self.start, self.treasure)

    # ── Dunder helpers ────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (f"Grid(rows={self.rows}, cols={self.cols}, "
                f"walls={len(self.walls)}, start={self.start}, "
                f"treasure={self.treasure})")
