"""Visualizer — renders the grid area with a clean, minimal aesthetic.

Rendering layers (back -> front):
  1. Background fill
  2. Open cells (slightly lighter than bg, NO grid lines — gap between cells is the separator)
  3. Explored cells — solid transparent fill at 35% opacity per agent, blended/layered
  4. Final paths — full-opacity colored cells on top of explored area
  5. Walls — solid dark gray blocks
  6. Start marker — small green square
  7. Treasure marker — small red diamond/square with subtle pulse
  8. Current node highlights
"""

import math
import pygame
from game.constants import (
    COLORS, GRID_W, GRID_H, GRID_COLS, GRID_ROWS,
    CELL_W, CELL_H, CELL_GAP, EXPLORED_ALPHA,
)


class Visualizer:
    """Renders the grid area (x=0..GRID_W, y=0..GRID_H) on *surface*."""

    def __init__(self, surface: pygame.Surface, grid):
        self.surface    = surface
        self.grid       = grid
        self._clip_rect = pygame.Rect(0, 0, GRID_W, GRID_H)

        # Pre-build per-agent explored surfaces (reused each frame)
        from game.constants import AGENT_CONFIGS
        self._agent_colors = [cfg['color'] for cfg in AGENT_CONFIGS]

    def set_grid(self, grid):
        self.grid = grid

    def draw(self, agents: list, tick: int, grid=None):
        if grid is not None:
            self.grid = grid

        g   = self.grid
        sur = self.surface

        # 1. Background
        sur.fill(COLORS['bg'], self._clip_rect)

        # 2. Open cells (no grid lines — the bg gap IS the separator)
        for r in range(g.rows):
            for c in range(g.cols):
                if not g.is_wall((r, c)):
                    rect = self._cell_inner_rect(r, c)
                    pygame.draw.rect(sur, COLORS['open'], rect)

        # 3. Explored cells — solid fill at 35% opacity, layered per agent
        for agent in agents:
            if not agent.active or not agent.explored:
                continue
            exp_surf = pygame.Surface((CELL_W - CELL_GAP * 2, CELL_H - CELL_GAP * 2), pygame.SRCALPHA)
            exp_surf.fill((*agent.color, EXPLORED_ALPHA))
            for pos in agent.explored:
                rect = self._cell_inner_rect(pos[0], pos[1])
                sur.blit(exp_surf, rect.topleft)

        # 4. Final paths — full opacity colored cells
        for agent in agents:
            if agent.active and agent.status == 'found' and agent.path:
                path_surf = pygame.Surface((CELL_W - CELL_GAP * 2, CELL_H - CELL_GAP * 2), pygame.SRCALPHA)
                path_surf.fill((*agent.color, 255))
                for pos in agent.path:
                    rect = self._cell_inner_rect(pos[0], pos[1])
                    sur.blit(path_surf, rect.topleft)

        # 5. Walls — solid blocks
        for r in range(g.rows):
            for c in range(g.cols):
                if g.is_wall((r, c)):
                    rect = self._cell_inner_rect(r, c)
                    pygame.draw.rect(sur, COLORS['wall'], rect)

        # 6. Start marker — small green square centered in the cell
        self._draw_start(sur, g.start)

        # 7. Treasure marker — small red square/diamond with subtle pulse
        self._draw_treasure(sur, g.treasure, tick)

        # 8. Current node highlight
        for agent in agents:
            if agent.active and agent.status == 'searching' and agent.current:
                self._draw_current_node(sur, agent.current, agent.color, tick)

    def _draw_start(self, surface, pos):
        rect = self._cell_inner_rect(pos[0], pos[1])
        cx, cy = rect.centerx, rect.centery
        size = min(rect.width, rect.height) // 3
        start_rect = pygame.Rect(cx - size, cy - size, size * 2, size * 2)
        pygame.draw.rect(surface, COLORS['start'], start_rect)

    def _draw_treasure(self, surface, pos, tick):
        rect = self._cell_inner_rect(pos[0], pos[1])
        cx, cy = rect.centerx, rect.centery
        # Subtle pulse animation
        pulse = 0.85 + 0.15 * math.sin(tick * 0.08)
        size = int(min(rect.width, rect.height) // 3 * pulse)
        # Small diamond
        pts = [(cx, cy - size), (cx + size, cy),
               (cx, cy + size), (cx - size, cy)]
        pygame.draw.polygon(surface, COLORS['treasure'], pts)

    def _draw_current_node(self, surface, pos, color, tick):
        rect = self._cell_inner_rect(pos[0], pos[1])
        pulse = 0.6 + 0.4 * math.sin(tick * 0.2)
        alpha = int(180 * pulse)
        cs = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        cs.fill((*color, alpha))
        surface.blit(cs, rect.topleft)

    def _cell_inner_rect(self, row, col):
        """Cell rect with gap for visual separation (no grid lines)."""
        x = col * CELL_W + CELL_GAP
        y = row * CELL_H + CELL_GAP
        w = CELL_W - CELL_GAP * 2
        h = CELL_H - CELL_GAP * 2
        return pygame.Rect(x, y, w, h)
