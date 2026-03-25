"""
Game Screen — the main racing visualisation screen.

Responsibilities:
  - Start all active agents' searches simultaneously
  - Step each search generator SPEEDS[speed_idx] times per frame
  - Detect the first agent to finish (winner_first) and shortest path (winner_shortest)
  - Hand off to ResultsScreen when all active agents have finished
  - Render grid via Visualizer, stats via StatsPanel, bottom bar with controls

Controls handled here:
  SPACE     — Pause / Resume
  R         — Restart same map
  N         — New random map (map_idx=3)
  1-4       — Toggle agent active state
  + / =     — Increase speed
  - / _     — Decrease speed
  E         — Open Map Editor
  TAB       — Jump to Results (when race done)
  ESC       — Back to title
"""

import pygame
from game.constants import (
    WINDOW_W, WINDOW_H, GRID_W, GRID_H, BOTTOM_BAR_H,
    COLORS, SPEEDS, AGENT_CONFIGS, GRID_ROWS, GRID_COLS,
    STATE_TITLE, STATE_RESULTS, STATE_EDITOR,
    MAP_NAMES,
)
from game.visualizer import Visualizer
from game.stats_panel import StatsPanel
from game.agent import Agent
from game.grid import Grid
from game.maps import get_map


class GameScreen:
    """Main game loop screen — agents race to find the treasure."""

    def __init__(self, surface: pygame.Surface, state_dict: dict):
        self.surface    = surface
        self.state      = state_dict
        self.tick       = 0

        # Pull state references
        self.agents     = state_dict['agents']
        self.grid       = state_dict['grid']

        # Renderers
        self.viz        = Visualizer(surface, self.grid)
        self.panel      = StatsPanel(surface)

        # Bottom bar font
        self._init_fonts()

        # Start all active agents
        self._start_searches()

        # Race tracking
        self._all_done        = False
        self._done_timer      = 0       # frames elapsed since all done
        self._pending_trans   = None    # queued state transition from update()

    # ------------------------------------------------------------------

    def _init_fonts(self):
        def _f(size, bold=False):
            for fam in ('consolas', 'monospace', None):
                try:
                    return pygame.font.SysFont(fam, size, bold=bold)
                except Exception:
                    pass
            return pygame.font.Font(None, size)
        self.font_bar     = _f(15, bold=True)
        self.font_bar_val = _f(15)

    def _start_searches(self):
        """Initialise and start the search generator for every active agent."""
        for agent in self.agents:
            if agent.active:
                agent.start_search(self.grid)

    # ------------------------------------------------------------------
    # Screen protocol
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event):
        # Drain any auto-transition queued by update()
        if self._pending_trans:
            t = self._pending_trans
            self._pending_trans = None
            return t

        state = self.state
        if event.type == pygame.KEYDOWN:
            key = event.key

            if key == pygame.K_ESCAPE:
                return STATE_TITLE

            if key == pygame.K_SPACE:
                state['paused'] = not state['paused']

            if key == pygame.K_r:
                return self._restart()

            if key == pygame.K_n:
                state['map_idx'] = 3
                map_data = get_map(3)
                state['grid'] = Grid(GRID_ROWS, GRID_COLS,
                                     map_data['walls'],
                                     map_data['start'],
                                     map_data['treasure'])
                self._rebuild_agents()
                return self._restart_in_place()

            if key == pygame.K_e:
                return STATE_EDITOR

            if key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                state['speed_idx'] = min(state['speed_idx'] + 1, len(SPEEDS) - 1)
            if key in (pygame.K_MINUS, pygame.K_UNDERSCORE, pygame.K_KP_MINUS):
                state['speed_idx'] = max(state['speed_idx'] - 1, 0)

            # Agent toggles 1-4
            for i, kcode in enumerate((pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4)):
                if key == kcode and i < len(self.agents):
                    self.agents[i].toggle_active()

            # Skip to results when done
            if key == pygame.K_TAB and self._all_done:
                return STATE_RESULTS

        return None

    def update(self, dt: float):
        self.tick += 1

        if self.state['paused'] or self._all_done:
            if self._all_done:
                self._done_timer += 1
                # Auto-advance to Results after 3 seconds (180 frames at 60 FPS)
                if self._done_timer >= 180:
                    self._pending_trans = STATE_RESULTS
            return

        steps = SPEEDS[self.state['speed_idx']]
        for _ in range(steps):
            self._step_all_agents()

        active = [a for a in self.agents if a.active]
        if active and all(a.status in ('found', 'failed') for a in active):
            self._all_done = True
            self._record_winners()

    def draw(self):
        self.surface.fill(COLORS['bg'])

        # Grid area
        self.viz.draw(self.agents, self.tick, grid=self.grid)

        # Stats panel
        self.panel.draw(
            self.agents, self.tick,
            self.state['speed_idx'],
            self.state['paused'],
        )

        # Bottom bar
        self._draw_bottom_bar()

        # Done overlay (banner + countdown bar)
        if self._all_done:
            self._draw_done_overlay()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _step_all_agents(self):
        """Advance every searching agent by one node expansion."""
        for agent in self.agents:
            if agent.active and agent.status == 'searching':
                agent.step()

    def _record_winners(self):
        """Record first-finder and shortest-path winner in shared state."""
        found = [a for a in self.agents if a.active and a.status == 'found']
        if not found:
            return

        fastest  = min(found, key=lambda a: a.time_taken)
        fastest.first_found = True
        self.state['winner_first'] = fastest.name

        shortest = min(found, key=lambda a: a.path_length)
        self.state['winner_shortest'] = shortest.name

    def _restart(self):
        """Rebuild grid + agents and re-run the same map in place."""
        idx      = self.state['map_idx']
        map_data = get_map(idx) if idx < 4 else None
        if map_data:
            self.state['grid'] = Grid(GRID_ROWS, GRID_COLS,
                                      map_data['walls'],
                                      map_data['start'],
                                      map_data['treasure'])
        self._rebuild_agents()
        return self._restart_in_place()

    def _rebuild_agents(self):
        agents = []
        for i, cfg in enumerate(AGENT_CONFIGS):
            a        = Agent(cfg['name'], cfg['algo_key'], cfg['color'])
            a.active = self.state['active_agents'][i]
            agents.append(a)
        self.state['agents']          = agents
        self.state['winner_first']    = ''
        self.state['winner_shortest'] = ''
        self.state['paused']          = False
        self.agents = agents

    def _restart_in_place(self):
        """Reset timing/viz without a screen transition."""
        self.grid          = self.state['grid']
        self.agents        = self.state['agents']
        self.viz           = Visualizer(self.surface, self.grid)
        self._all_done     = False
        self._done_timer   = 0
        self._pending_trans = None
        self._start_searches()
        return None   # stay on this screen

    # ------------------------------------------------------------------
    # Bottom bar
    # ------------------------------------------------------------------

    def _draw_bottom_bar(self):
        bar_rect = pygame.Rect(0, GRID_H, GRID_W, BOTTOM_BAR_H)
        pygame.draw.rect(self.surface, COLORS['panel_bg'], bar_rect)
        pygame.draw.line(self.surface, COLORS['panel_border'],
                         (0, GRID_H), (GRID_W, GRID_H), 1)

        items = [
            ('[SPC] Pause',  COLORS['highlight']),
            ('[R] Restart',  COLORS['text_secondary']),
            ('[N] New Map',  COLORS['text_secondary']),
            ('[1-4] Toggle', COLORS['text_secondary']),
            ('[+/-] Speed',  COLORS['text_secondary']),
            ('[E] Editor',   COLORS['text_secondary']),
            ('[ESC] Menu',   COLORS['text_dim']),
        ]

        x = 12
        y = GRID_H + (BOTTOM_BAR_H - self.font_bar.get_height()) // 2
        for text, color in items:
            s = self.font_bar.render(text, True, color)
            self.surface.blit(s, (x, y))
            x += s.get_width() + 22

        map_name = MAP_NAMES[min(self.state['map_idx'], len(MAP_NAMES) - 1)]
        ms = self.font_bar_val.render(f'Map: {map_name}', True, COLORS['text_dim'])
        self.surface.blit(ms, ms.get_rect(right=GRID_W - 12, y=y))

    # ------------------------------------------------------------------
    # Done overlay
    # ------------------------------------------------------------------

    def _draw_done_overlay(self):
        """Semi-transparent banner + countdown progress bar when race is done."""
        wait_frames = 180

        # Countdown progress bar at base of the grid
        frac  = min(self._done_timer / wait_frames, 1.0)
        bar_w = int(GRID_W * frac)
        pygame.draw.rect(self.surface, COLORS['success'],
                         pygame.Rect(0, GRID_H - 4, bar_w, 4))

        # Banner
        banner_h = 66
        banner_y = GRID_H // 2 - banner_h // 2
        bs = pygame.Surface((GRID_W, banner_h), pygame.SRCALPHA)
        bs.fill((0, 0, 0, 165))
        self.surface.blit(bs, (0, banner_y))

        wf    = self.state.get('winner_first', '')
        ws    = self.state.get('winner_shortest', '')
        lines = []
        if wf:
            lines.append(f'First to finish: {wf}')
        if ws and ws != wf:
            lines.append(f'Shortest path:   {ws}')
        lines.append('[Tab] Results now   |   Auto-advancing…')

        y0 = banner_y + 8
        for line in lines:
            ls = self.font_bar.render(line, True, COLORS['text_primary'])
            self.surface.blit(ls, ls.get_rect(centerx=GRID_W // 2, y=y0))
            y0 += self.font_bar.get_height() + 4
