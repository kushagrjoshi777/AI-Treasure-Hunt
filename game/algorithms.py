"""
Search algorithms for the AI Treasure Hunt game.

Each algorithm is implemented as a generator function that yields one state dict
per node expansion, enabling step-by-step visualization in the UI.

Yielded state dict schema
--------------------------
{
    'current'  : (row, col) | None   — the node just popped/expanded, None if finished
    'explored' : set                  — all nodes whose neighbors have been examined
    'frontier' : list                 — nodes currently waiting to be expanded
    'path'     : None | list          — None while searching; [] if no path found;
                                        [(r,c), ...] start→goal if found
    'done'     : bool                 — True on the final yield
    'found'    : bool                 — True only when a path was found
}
"""

from collections import deque
import heapq


# ──────────────────────────────────────────────────────────────────────────────
# Internal helper
# ──────────────────────────────────────────────────────────────────────────────

def _reconstruct_path(came_from: dict, start: tuple, goal: tuple) -> list:
    """
    Walk *came_from* backwards from *goal* to *start* and return the ordered
    path [start, ..., goal].

    Parameters
    ----------
    came_from : dict
        Maps each node to the node it was reached from.
    start : tuple
        The starting (row, col).
    goal : tuple
        The goal (row, col).

    Returns
    -------
    list of (row, col)
    """
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from.get(node)
    path.reverse()
    # Sanity: if reconstruction is broken the path may not start at start.
    if path and path[0] != start:
        return []
    return path


def _snapshot(current, explored, frontier_nodes, path, done, found):
    """Build a standardised state snapshot for the visualiser."""
    return {
        'current' : current,
        'explored': set(explored),        # copy so the caller can mutate freely
        'frontier': list(frontier_nodes),
        'path'    : path,
        'done'    : done,
        'found'   : found,
    }


# ──────────────────────────────────────────────────────────────────────────────
# BFS
# ──────────────────────────────────────────────────────────────────────────────

def bfs_search(grid, start: tuple, goal: tuple):
    """
    Breadth-First Search — layer-by-layer expansion using a FIFO queue.

    Properties
    ----------
    Complete  : Yes — will always find a path if one exists.
    Optimal   : Yes — always finds the *shortest* path (fewest edges).
    Time      : O(V + E) where V = cells, E = edges between cells.
    Space     : O(V) — frontier can hold an entire grid layer.

    Because BFS expands nodes in order of increasing depth, it touches many
    more cells than A* on open grids but is guaranteed to be optimal.
    """
    # ── trivial case ──────────────────────────────────────────────────────────
    if start == goal:
        yield _snapshot(start, {start}, [], [start], done=True, found=True)
        return

    # ── initialise ────────────────────────────────────────────────────────────
    queue     = deque([start])
    came_from = {start: None}   # also acts as the visited set
    explored  = set()           # nodes fully expanded (popped from queue)

    while queue:
        current = queue.popleft()
        explored.add(current)

        # yield state *before* checking if we reached the goal so the
        # visualiser can colour the goal cell when it is finally expanded.
        frontier_nodes = list(queue)
        yield _snapshot(current, explored, frontier_nodes,
                        path=None, done=False, found=False)

        if current == goal:
            path = _reconstruct_path(came_from, start, goal)
            yield _snapshot(current, explored, [], path, done=True, found=True)
            return

        for neighbor in grid.get_neighbors(current):
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)

    # Queue exhausted — no path exists.
    yield _snapshot(None, explored, [], [], done=True, found=False)


# ──────────────────────────────────────────────────────────────────────────────
# DFS
# ──────────────────────────────────────────────────────────────────────────────

def dfs_search(grid, start: tuple, goal: tuple):
    """
    Depth-First Search — deep exploration using a LIFO stack.

    Properties
    ----------
    Complete  : Yes (on finite graphs with visited tracking).
    Optimal   : No — the first path found may be much longer than the shortest.
    Time      : O(V + E).
    Space     : O(V) worst case, but typically much less than BFS.

    DFS will dive deep into one branch before backtracking.  On maps with many
    dead ends it can explore large swathes of the grid before backtracking,
    making it easy to visualise how it gets "lost" compared to BFS/A*.
    """
    if start == goal:
        yield _snapshot(start, {start}, [], [start], done=True, found=True)
        return

    # Stack stores (node, came_from_parent) tuples so we can record the path.
    # Using an explicit stack (not Python recursion) avoids stack-overflow on
    # large grids and lets us yield between steps.
    stack     = [start]
    came_from = {start: None}
    explored  = set()

    while stack:
        current = stack.pop()

        # Skip if already fully expanded (can happen because DFS may push the
        # same node multiple times via different paths before it is expanded).
        if current in explored:
            continue

        explored.add(current)
        frontier_nodes = list(stack)
        yield _snapshot(current, explored, frontier_nodes,
                        path=None, done=False, found=False)

        if current == goal:
            path = _reconstruct_path(came_from, start, goal)
            yield _snapshot(current, explored, [], path, done=True, found=True)
            return

        # Push neighbors in reverse order so the "first" neighbor is expanded
        # first (consistent left-to-right, top-to-bottom behaviour).
        for neighbor in reversed(grid.get_neighbors(current)):
            if neighbor not in explored and neighbor not in came_from:
                came_from[neighbor] = current
                stack.append(neighbor)

    yield _snapshot(None, explored, [], [], done=True, found=False)


# ──────────────────────────────────────────────────────────────────────────────
# A*
# ──────────────────────────────────────────────────────────────────────────────

def _manhattan(a: tuple, b: tuple) -> int:
    """Manhattan distance heuristic — admissible for 4-directional grids."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar_search(grid, start: tuple, goal: tuple):
    """
    A* Search — best-first search using f = g + h (cost + heuristic).

    Properties
    ----------
    Complete  : Yes.
    Optimal   : Yes — with an admissible & consistent heuristic (Manhattan
                distance satisfies both conditions on 4-directional grids).
    Time      : O(E log V) with a binary heap.
    Space     : O(V).

    The Manhattan distance heuristic guides the search directly toward the
    goal, dramatically reducing the number of nodes expanded compared to BFS
    while still guaranteeing the shortest path.
    """
    if start == goal:
        yield _snapshot(start, {start}, [], [start], done=True, found=True)
        return

    # Min-heap entries: (f_score, g_score, node)
    # g_score = actual cost from start; f_score = g + h
    h_start  = _manhattan(start, goal)
    heap     = [(h_start, 0, start)]
    came_from = {start: None}
    g_score  = {start: 0}
    explored = set()

    while heap:
        f, g, current = heapq.heappop(heap)

        if current in explored:
            continue

        explored.add(current)
        frontier_nodes = [entry[2] for entry in heap]
        yield _snapshot(current, explored, frontier_nodes,
                        path=None, done=False, found=False)

        if current == goal:
            path = _reconstruct_path(came_from, start, goal)
            yield _snapshot(current, explored, [], path, done=True, found=True)
            return

        for neighbor in grid.get_neighbors(current):
            if neighbor in explored:
                continue
            tentative_g = g + 1  # uniform edge cost = 1
            if tentative_g < g_score.get(neighbor, float('inf')):
                g_score[neighbor]   = tentative_g
                came_from[neighbor] = current
                f_new = tentative_g + _manhattan(neighbor, goal)
                heapq.heappush(heap, (f_new, tentative_g, neighbor))

    yield _snapshot(None, explored, [], [], done=True, found=False)


# ──────────────────────────────────────────────────────────────────────────────
# Greedy Best-First Search
# ──────────────────────────────────────────────────────────────────────────────

def greedy_search(grid, start: tuple, goal: tuple):
    """
    Greedy Best-First Search — expands the node that *looks* closest to the
    goal according to the heuristic, ignoring actual path cost.

    Properties
    ----------
    Complete  : Yes (on finite graphs with visited tracking).
    Optimal   : No — greedy ignores accumulated cost and may find a longer path.
    Time      : O(E log V).
    Space     : O(V).

    Greedy is often very fast in practice because it rushes toward the goal,
    but it can be fooled by obstacles that force long detours.  Comparing its
    path against A* clearly demonstrates why accounting for path cost matters.
    """
    if start == goal:
        yield _snapshot(start, {start}, [], [start], done=True, found=True)
        return

    # Min-heap entries: (h_score, node)
    heap      = [(_manhattan(start, goal), start)]
    came_from = {start: None}
    explored  = set()

    while heap:
        h, current = heapq.heappop(heap)

        if current in explored:
            continue

        explored.add(current)
        frontier_nodes = [entry[1] for entry in heap]
        yield _snapshot(current, explored, frontier_nodes,
                        path=None, done=False, found=False)

        if current == goal:
            path = _reconstruct_path(came_from, start, goal)
            yield _snapshot(current, explored, [], path, done=True, found=True)
            return

        for neighbor in grid.get_neighbors(current):
            if neighbor not in explored and neighbor not in came_from:
                came_from[neighbor] = current
                heapq.heappush(heap, (_manhattan(neighbor, goal), neighbor))

    yield _snapshot(None, explored, [], [], done=True, found=False)
