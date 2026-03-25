"""
AI Treasure Hunt — Main Entry Point
21CSC206T Artificial Intelligence Project

Four AI agents race to find treasure using different search algorithms:
  BFS (Blue)      — Breadth-First Search, guarantees shortest path
  DFS (Red)       — Depth-First Search, memory efficient, not optimal
  A* (Teal)       — Heuristic search, f=g+h, optimal and efficient
  Greedy (Orange) — f=h only, fast but not optimal

Controls:
  SPACE      — Pause/Resume
  R          — Restart with same map
  N          — New random map
  1-4        — Toggle agents on/off
  + / -      — Speed up / slow down
  E          — Open map editor
  ESC        — Back to menu
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pygame
from game.constants import (
    WINDOW_W, WINDOW_H, FPS, GRID_ROWS, GRID_COLS,
    AGENT_CONFIGS, DEFAULT_SPEED_IDX,
    STATE_TITLE, STATE_SELECT_MAP, STATE_GAME,
    STATE_RESULTS, STATE_EDITOR, STATE_QUIT,
)
from game.agent import Agent
from game.grid import Grid
from game.maps import get_map

from screens.title_screen import TitleScreen
from screens.select_map_screen import SelectMapScreen
from screens.game_screen import GameScreen
from screens.results_screen import ResultsScreen
from screens.editor_screen import EditorScreen


def make_initial_state():
    """Create the shared state dictionary passed between all screens."""
    map_data = get_map(0)
    grid = Grid(
        GRID_ROWS, GRID_COLS,
        map_data['walls'],
        map_data['start'],
        map_data['treasure'],
    )
    agents = [
        Agent(cfg['name'], cfg['algo_key'], cfg['color'])
        for cfg in AGENT_CONFIGS
    ]
    return {
        'map_idx'        : 0,
        'active_agents'  : [True, True, True, True],
        'grid'           : grid,
        'agents'         : agents,
        'speed_idx'      : DEFAULT_SPEED_IDX,
        'paused'         : False,
        'winner_first'   : '',
        'winner_shortest': '',
        'custom_grid'    : None,
    }


class ScreenManager:
    """Manages screen transitions and the shared game state."""

    SCREEN_MAP = {
        STATE_TITLE      : TitleScreen,
        STATE_SELECT_MAP : SelectMapScreen,
        STATE_GAME       : GameScreen,
        STATE_RESULTS    : ResultsScreen,
        STATE_EDITOR     : EditorScreen,
    }

    def __init__(self, surface: pygame.Surface):
        self.surface    = surface
        self.state_dict = make_initial_state()
        self.current    = TitleScreen(surface, self.state_dict)
        self.clock      = pygame.time.Clock()

    def transition_to(self, state_name: str):
        cls = self.SCREEN_MAP.get(state_name)
        if cls:
            self.current = cls(self.surface, self.state_dict)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                result = self.current.handle_event(event)
                if result == STATE_QUIT:
                    running = False
                    break
                elif result is not None:
                    self.transition_to(result)

            if not running:
                break

            self.current.update(dt)
            self.current.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit(0)


def main():
    pygame.init()
    pygame.display.set_caption('AI Treasure Hunt — 21CSC206T Artificial Intelligence')
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))

    # Try to set a window icon (skip if assets not present)
    try:
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(icon, (255, 215, 0), (16, 16), 14)
        pygame.draw.circle(icon, (255, 237, 74), (16, 16), 8)
        pygame.display.set_icon(icon)
    except Exception:
        pass

    manager = ScreenManager(screen)
    manager.run()


if __name__ == '__main__':
    main()
