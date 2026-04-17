"""
Predefined and procedurally generated maps for the AI Treasure Hunt game.

All maps target a 20-row × 30-column grid.  Every map function returns a dict:

    {
        'walls'    : set of (row, col),
        'start'    : (row, col),
        'treasure' : (row, col),
        'name'     : str,
    }

Public API
----------
get_map(map_idx)              — return map dict for the given index (0-3)
generate_random_map(rows, cols) — procedural randomised-DFS perfect maze
"""

import random


# ──────────────────────────────────────────────────────────────────────────────
# Shared constants (kept local to avoid circular imports)
# ──────────────────────────────────────────────────────────────────────────────

_ROWS = 20
_COLS = 30


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────

def get_map(map_idx: int) -> dict:
    """
    Return a map dict for *map_idx*.

    Indices
    -------
    0 → Simple Open
    1 → Maze Corridors
    2 → Dead End Traps
    3 → Random Maze (procedurally generated, fresh each call)

    Raises
    ------
    ValueError if map_idx is not in [0, 3].
    """
    if map_idx == 3:
        return generate_random_map(_ROWS, _COLS)
    generators = [_map_simple, _map_maze, _map_deadends]
    if 0 <= map_idx < len(generators):
        return generators[map_idx]()
    raise ValueError(f"map_idx must be 0-3, got {map_idx!r}")


# ──────────────────────────────────────────────────────────────────────────────
# Internal wall-building helpers
# ──────────────────────────────────────────────────────────────────────────────

def _hwall(walls: set, row: int, col_start: int, length: int) -> None:
    """Add a horizontal run of *length* wall cells starting at (row, col_start)."""
    for c in range(col_start, col_start + length):
        walls.add((row, c))


def _vwall(walls: set, col: int, row_start: int, length: int) -> None:
    """Add a vertical run of *length* wall cells starting at (row_start, col)."""
    for r in range(row_start, row_start + length):
        walls.add((r, col))


# ──────────────────────────────────────────────────────────────────────────────
# Map 0 — Simple Open
# ──────────────────────────────────────────────────────────────────────────────

def _map_simple() -> dict:
    """
    A mostly open grid with scattered wall blobs (~80 wall cells).

    Design goals
    ~~~~~~~~~~~~
    * All four algorithms find a path — no complete blockades.
    * Obstacles are spread across the grid so there are interesting detours but
      multiple routes always exist.
    * Good for a first look: wave-front (BFS) vs. directed (A*/Greedy) is
      clearly visible even on this easy map.

    Layout  (. = open, # = wall, S = start, T = treasure)
    ~~~~~~
    T near (1, 28) top-right; S near (18, 1) bottom-left.
    """
    walls: set = set()

    # ── Upper-left cluster (rows 2-5, cols 3-8) ──────────────────────────────
    _hwall(walls, 2,  4, 5)   # (2,4)-(2,8)
    _hwall(walls, 3,  4, 4)   # (3,4)-(3,7)
    _hwall(walls, 4,  4, 3)   # (4,4)-(4,6)
    _vwall(walls, 8,  2, 4)   # (2,8)-(5,8)

    # ── Upper-centre horizontal blocker (rows 2-3, cols 12-17) ───────────────
    _hwall(walls, 2, 12, 6)   # (2,12)-(2,17)
    _hwall(walls, 3, 12, 5)   # (3,12)-(3,16)

    # ── Mid-left barrier (rows 7-8, cols 2-6) ────────────────────────────────
    _hwall(walls, 7,  2, 6)   # (7,2)-(7,7)
    _hwall(walls, 8,  2, 4)   # (8,2)-(8,5)

    # ── Centre island (rows 9-11, cols 13-17) ────────────────────────────────
    _hwall(walls, 9,  13, 5)  # (9,13)-(9,17)
    _hwall(walls, 10, 13, 5)  # (10,13)-(10,17)
    _hwall(walls, 11, 13, 4)  # (11,13)-(11,16)
    _vwall(walls, 13,  9, 3)  # (9,13)-(11,13) left edge
    _vwall(walls, 17,  9, 3)  # (9,17)-(11,17) right edge

    # ── Right-side column pair (rows 5-7, cols 22-25) ────────────────────────
    _hwall(walls,  5, 22, 4)  # (5,22)-(5,25)
    _hwall(walls,  6, 22, 4)  # (6,22)-(6,25)

    # ── Lower-centre barrier (rows 14-15, cols 7-12) ─────────────────────────
    _hwall(walls, 14,  7, 6)  # (14,7)-(14,12)
    _hwall(walls, 15,  7, 5)  # (15,7)-(15,11)

    # ── Lower-right scatter (rows 13-14, cols 20-24) ─────────────────────────
    _hwall(walls, 13, 20, 5)  # (13,20)-(13,24)
    _hwall(walls, 14, 20, 4)  # (14,20)-(14,23)

    # ── Near-start scatter (rows 16-17, cols 3-8) ────────────────────────────
    _hwall(walls, 16,  3, 3)  # (16,3)-(16,5)
    _hwall(walls, 17,  5, 4)  # (17,5)-(17,8)

    # ── Near-treasure scatter (rows 4-5, cols 24-26) ─────────────────────────
    _hwall(walls,  4, 24, 3)  # (4,24)-(4,26)
    _hwall(walls,  5, 24, 2)  # (5,24)-(5,25)

    # ── Additional vertical pillars ───────────────────────────────────────────
    _vwall(walls,  6,  4, 4)  # (4,6)-(7,6)  — left pillar
    _vwall(walls, 18,  6, 5)  # (6,18)-(10,18) — centre-right pillar
    _vwall(walls, 25,  8, 4)  # (8,25)-(11,25) — right barrier
    _vwall(walls, 10, 12, 5)  # (12,10)-(16,10) — lower pillar
    _vwall(walls, 15,  3, 3)  # (3,15)-(5,15)
    _vwall(walls, 20, 10, 4)  # (10,20)-(13,20)

    start    = (18, 1)
    treasure = (1, 28)
    walls.discard(start)
    walls.discard(treasure)

    return {'walls': walls, 'start': start, 'treasure': treasure,
            'name': 'Simple Open'}


# ──────────────────────────────────────────────────────────────────────────────
# Map 1 — Maze Corridors
# ──────────────────────────────────────────────────────────────────────────────

def _map_maze() -> dict:
    """
    A hand-crafted maze with long, narrow corridors and 200+ wall cells.

    Design goals
    ~~~~~~~~~~~~
    * BFS explores cells layer-by-layer — visibly broader than A*.
    * DFS dives deep into corridors and may find a very long, winding path.
    * Narrow single-cell passages force algorithms to commit before seeing
      what is beyond, making the differences vivid.

    Structure
    ~~~~~~~~~
    Horizontal walls at even rows create a layered comb maze.  Each row-wall
    spans most of the grid width with deliberate single/double-cell gaps on
    alternating sides.  Vertical dividers further segment the grid into rooms
    connected by small openings.
    """
    walls: set = set()

    # ── Full-width horizontal walls at even rows with deliberate openings ─────
    # Format: (wall_row, set_of_open_cols)
    horizontal_layers = [
        (2,  {14, 15}),          # centre gap → upper section
        (4,  { 4,  5, 24, 25}),  # left + right gaps
        (6,  {10, 11, 20, 21}),  # centre-left + centre-right
        (8,  { 2,  3, 16, 17}),  # far-left + centre
        (10, { 6,  7, 22, 23}),  # left-of-centre + right-of-centre
        (12, {12, 13, 26, 27}),  # centre + right
        (14, { 4,  5, 18, 19}),  # left + right-of-centre
        (16, {10, 11, 24, 25}),  # centre-left + right
        (18, {16, 17}),          # near-start exit
    ]

    for wall_row, open_cols in horizontal_layers:
        for c in range(1, _COLS - 1):   # leave col 0 and col 29 as border
            if c not in open_cols:
                walls.add((wall_row, c))

    # ── Vertical dividers creating corridor chambers ──────────────────────────
    # Format: (col, row_start, row_end_inclusive, set_of_open_rows)
    vertical_dividers = [
        ( 7,  1, 17, { 3,  4,  9, 10, 15}),
        (14,  1, 17, { 5,  6, 11, 12, 13}),
        (21,  1, 17, { 7,  8, 13, 14, 15}),
    ]

    for col, r_start, r_end, open_rows in vertical_dividers:
        for r in range(r_start, r_end + 1):
            if r not in open_rows:
                walls.add((r, col))

    start    = (18, 1)
    treasure = (1, 28)
    walls.discard(start)
    walls.discard(treasure)

    return {'walls': walls, 'start': start, 'treasure': treasure,
            'name': 'Maze Corridors'}


# ──────────────────────────────────────────────────────────────────────────────
# Map 2 — Dead End Traps
# ──────────────────────────────────────────────────────────────────────────────

def _map_deadends() -> dict:
    """
    Multiple tempting dead-end corridors with only one true path to the
    treasure, designed to punish DFS and highlight backtracking.

    Design goals
    ~~~~~~~~~~~~
    * DFS is likely to enter multiple dead ends and must backtrack repeatedly.
    * BFS avoids dead ends efficiently via its wave-front expansion.
    * A*/Greedy mostly skip dead ends that point away from the goal.

    Structure
    ~~~~~~~~~
    A central horizontal spine wall at row 9 divides the grid.  Only a single
    cell gap at col 15 connects the lower half (start side) to the upper half
    (treasure side).  Several U-shaped dead-end corridors hang off the spine
    on both sides to trap algorithms that are not guided by good heuristics.
    """
    walls: set = set()

    # ── Central spine — full horizontal wall at row 9, gap only at col 15 ────
    for c in range(1, _COLS - 1):
        if c != 15:
            walls.add((9, c))

    # ── Helper: U-shaped dead-end finger pointing downward ────────────────────
    # The corridor opens at the top (toward the spine) and is sealed at the bottom.
    def add_finger_down(col_center: int, depth: int) -> None:
        top_row = 10
        for r in range(top_row, top_row + depth):
            walls.add((r, col_center - 1))   # left wall
            walls.add((r, col_center + 1))   # right wall
        # Bottom cap (3 cells wide)
        for c in (col_center - 1, col_center, col_center + 1):
            walls.add((top_row + depth, c))

    add_finger_down(col_center=5,  depth=5)   # far-left dead end
    add_finger_down(col_center=11, depth=4)   # centre-left dead end
    add_finger_down(col_center=20, depth=6)   # centre-right dead end
    add_finger_down(col_center=26, depth=3)   # far-right dead end

    # ── Helper: U-shaped dead-end finger pointing upward ─────────────────────
    # The corridor opens at the bottom (just above the spine gap) and is sealed
    # at the top.
    def add_finger_up(col_center: int, depth: int) -> None:
        bottom_row = 8
        for r in range(bottom_row - depth, bottom_row + 1):
            walls.add((r, col_center - 1))
            walls.add((r, col_center + 1))
        # Top cap
        for c in (col_center - 1, col_center, col_center + 1):
            walls.add((bottom_row - depth - 1, c))

    add_finger_up(col_center=4,  depth=3)   # upper-left trap
    add_finger_up(col_center=22, depth=4)   # upper-right trap

    # ── Lower-half scatter to make paths less trivial ─────────────────────────
    scatter_lower = [
        (13, 3), (13, 4), (13, 5),
        (14, 3),
        (15, 6), (15, 7), (15, 8),
        (12, 23), (12, 24),
        (13, 23),
        (16, 24), (16, 25), (16, 26),
        (14, 14), (14, 15), (14, 16),
        (15, 14),
        (17, 10), (17, 11),
    ]
    for pos in scatter_lower:
        walls.add(pos)

    # ── Upper-half partial blocker — funnels agents rightward ─────────────────
    # Row 5: wall from col 16 to col 23, one gap at col 20 to allow passage.
    for c in range(16, 24):
        walls.add((5, c))
    walls.discard((5, 20))   # only gap — forces agents to find it

    # ── Additional upper scatter ───────────────────────────────────────────────
    upper_scatter = [
        (3, 18), (3, 19), (3, 20),
        (4, 18),
        (2,  8), (2,  9), (2, 10),
        (3,  8),
    ]
    for pos in upper_scatter:
        walls.add(pos)

    start    = (18, 1)
    treasure = (1, 28)
    walls.discard(start)
    walls.discard(treasure)

    return {'walls': walls, 'start': start, 'treasure': treasure,
            'name': 'Dead End Traps'}


# ──────────────────────────────────────────────────────────────────────────────
# Map 3 — Random Maze (procedural)
# ──────────────────────────────────────────────────────────────────────────────

def generate_random_map(rows: int, cols: int) -> dict:
    """
    Generate a perfect maze using iterative randomised DFS (recursive
    backtracker algorithm).

    Algorithm overview
    ------------------
    1. Initialise every grid cell as a wall.
    2. Treat cells at *even* (row, col) coordinates as "room" cells — they
       are separated by single wall cells which act as potential passages.
    3. Start a DFS from room (0, 0).  At each step pick a random unvisited
       room-neighbour, carve both the neighbour room *and* the wall cell
       between them.
    4. Continue until all room cells are visited.

    Result: a *perfect maze* — exactly one path exists between any two cells,
    no loops, all cells reachable.  This guarantees every algorithm terminates
    with a valid path.

    Room ↔ grid coordinate mapping
    --------------------------------
    Room (rr, rc) → grid (rr*2, rc*2).
    Wall between rooms (rr1,rc1) and (rr2,rc2) → ((rr1+rr2), (rc1+rc2)).

    Parameters
    ----------
    rows : int
        Total grid rows (ideally even for cleanest result; 20 works fine).
    cols : int
        Total grid cols (ideally even; 30 works fine).

    Returns
    -------
    dict with keys 'walls' (set), 'start' (tuple), 'treasure' (tuple),
    'name' (str).
    """
    # Number of logical room cells in each dimension
    room_rows = (rows - 1) // 2   # 9 for rows=20
    room_cols = (cols - 1) // 2   # 14 for cols=30

    # ── Start with the entire grid walled ────────────────────────────────────
    walls: set = set()
    for r in range(rows):
        for c in range(cols):
            walls.add((r, c))

    # ── Iterative randomised DFS ──────────────────────────────────────────────
    visited: set = set()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def room_grid(rr: int, rc: int) -> tuple:
        return rr * 2, rc * 2

    def carve_room(rr: int, rc: int) -> None:
        gr, gc = room_grid(rr, rc)
        walls.discard((gr, gc))

    # Begin from top-left room
    start_room = (0, 0)
    stack = [start_room]
    visited.add(start_room)
    carve_room(0, 0)

    while stack:
        rr, rc = stack[-1]

        # Collect all unvisited room-neighbours
        unvisited = []
        for drr, drc in directions:
            nrr, nrc = rr + drr, rc + drc
            if (0 <= nrr < room_rows
                    and 0 <= nrc < room_cols
                    and (nrr, nrc) not in visited):
                unvisited.append((nrr, nrc, drr, drc))

        if unvisited:
            # Pick a random unvisited neighbour and carve toward it
            nrr, nrc, drr, drc = random.choice(unvisited)
            visited.add((nrr, nrc))

            # Carve the wall cell *between* current room and chosen neighbour
            cur_gr, cur_gc = room_grid(rr, rc)
            walls.discard((cur_gr + drr, cur_gc + drc))

            # Carve the neighbour room itself
            carve_room(nrr, nrc)

            stack.append((nrr, nrc))
        else:
            stack.pop()

    # ── Place start and treasure in room cells ────────────────────────────────
    # Start  → bottom-left room: (room_rows-1, 0) → grid (rows-2, 0)
    # Treasure → top-right room: (0, room_cols-1) → grid (0, cols-2)
    start_r, start_c = room_grid(room_rows - 1, 0)
    treas_r, treas_c = room_grid(0, room_cols - 1)

    # Nudge start one column right to avoid sitting on col 0 if possible
    if start_c == 0 and cols > 2:
        walls.discard((start_r, start_c + 1))  # open adjacent passage cell
        start_c = start_c + 1                  # prefer col 1 for aesthetics

    start    = (start_r, start_c)
    treasure = (treas_r, treas_c)

    walls.discard(start)
    walls.discard(treasure)

    return {
        'walls'    : walls,
        'start'    : start,
        'treasure' : treasure,
        'name'     : 'Random Maze',
    }
