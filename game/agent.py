# -*- coding: utf-8 -*-
"""Agent class - wraps an AI search algorithm and tracks its state."""
import time
from game.algorithms import bfs_search, dfs_search, astar_search, greedy_search

# Map algo keys to their generator functions
ALGO_MAP = {
    'bfs':    bfs_search,
    'dfs':    dfs_search,
    'astar':  astar_search,
    'greedy': greedy_search,
}


class Agent:
    """One AI agent running a search algorithm on the grid.

    The agent wraps a search generator and exposes a step() method that
    advances it by one node per call. All accumulated state (explored set,
    frontier, path, timing) is stored here so the visualizer and stats panel
    can read it directly.
    """

    def __init__(self, name: str, algo_key: str, color: tuple):
        """Create an agent.

        Args:
            name:     Human-readable label shown in the UI, e.g. "BFS".
            algo_key: Key into ALGO_MAP, e.g. "bfs".
            color:    RGB tuple used for rendering this agent's cells/path.
        """
        self.name        = name       # "BFS", "DFS", "A*", "Greedy"
        self.algo_key    = algo_key   # "bfs", "dfs", "astar", "greedy"
        self.color       = color      # RGB tuple
        self.active      = True       # included in the race
        self.first_found = False      # set externally when this agent wins the race
        self.reset()

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    def reset(self):
        """Reset to idle state — call before starting a new search."""
        self.explored       = set()   # set of (row, col) already visited
        self.frontier       = []      # list of (row, col) pending visit
        self.path           = []      # list of (row, col) from start to goal
        self.current        = None    # (row, col) node being expanded right now
        self.status         = 'idle'  # idle | searching | found | failed
        self.nodes_explored = 0       # len(self.explored) snapshot
        self.path_length    = 0       # number of edges in final path
        self.time_start     = 0.0     # perf_counter at search start
        self.time_taken     = -1.0    # seconds elapsed when done; -1 = not done
        self._generator     = None    # the underlying search generator
        self.first_found    = False   # reset win badge

    # ------------------------------------------------------------------
    # Search lifecycle
    # ------------------------------------------------------------------

    def start_search(self, grid):
        """Initialize and start the search generator.

        Creates a fresh generator from the algorithm function and sets status
        to 'searching'. The grid provides start/treasure coordinates and the
        neighbor/wall logic needed by the algorithms.

        Args:
            grid: A Grid instance (see game/grid.py).
        """
        self.reset()
        fn = ALGO_MAP[self.algo_key]
        self._generator = fn(grid, grid.start, grid.treasure)
        self.status     = 'searching'
        self.time_start = time.perf_counter()

    def step(self) -> bool:
        """Advance the search by one node expansion.

        Pulls the next state dict from the generator and updates all instance
        attributes. When the generator signals done=True the final path (or
        failure) is recorded and the generator is exhausted.

        Returns:
            True  — search is finished (found or failed).
            False — search still in progress; call step() again next frame.
        """
        # Guard: do nothing if there is no active search
        if self._generator is None or self.status not in ('searching',):
            return True

        try:
            state = next(self._generator)

            # Mirror generator state into agent attributes
            self.explored       = state['explored']
            self.frontier       = state['frontier']
            self.current        = state['current']
            self.nodes_explored = len(self.explored)

            if state['done']:
                # Search concluded this step — record timing and outcome
                self.time_taken = time.perf_counter() - self.time_start

                if state['found']:
                    self.path        = state['path']
                    # path_length is number of *edges*, so subtract the start node
                    self.path_length = len(self.path) - 1 if self.path else 0
                    self.status      = 'found'
                else:
                    self.path   = []
                    self.status = 'failed'

                return True  # done

            return False  # still searching

        except StopIteration:
            # Generator exhausted without explicitly setting done=True
            self.time_taken = time.perf_counter() - self.time_start
            self.status     = 'failed'
            return True

    # ------------------------------------------------------------------
    # Convenience toggles
    # ------------------------------------------------------------------

    def toggle_active(self):
        """Flip the active flag; inactive agents are excluded from the race."""
        self.active = not self.active

    # ------------------------------------------------------------------
    # Display properties
    # ------------------------------------------------------------------

    @property
    def status_text(self) -> str:
        """Short human-readable status string for the stats panel."""
        if self.status == 'idle':      return 'Idle'
        if self.status == 'searching': return 'Searching...'
        if self.status == 'found':     return f'Found! ({self.path_length} steps)'
        if self.status == 'failed':    return 'No Path!'
        return ''

    @property
    def time_text(self) -> str:
        """Formatted elapsed/final time string.

        While searching shows a live counter; after done shows final value.
        """
        if self.time_taken < 0:
            # Not yet finished
            if self.status == 'searching':
                elapsed = time.perf_counter() - self.time_start
                return f'{elapsed:.2f}s'
            return '--'
        return f'{self.time_taken:.3f}s'

    def __repr__(self) -> str:
        return (
            f'<Agent name={self.name!r} status={self.status!r} '
            f'explored={self.nodes_explored} path_len={self.path_length}>'
        )
