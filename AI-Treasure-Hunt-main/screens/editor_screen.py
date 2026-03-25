"""
Map Editor Screen — lets the player draw custom walls on the grid.

Controls:
  Left-click drag  — place walls
  Right-click drag — erase walls
  S / Left-click S — place start marker
  T / Left-click T — place treasure marker
  C                — clear all walls
  [Enter]          — save and launch game with this custom grid
  [ESC]            — discard and return to select-map screen

The editor stores the finished grid in state_dict['custom_grid'] and sets
state_dict['map_idx'] to a sentinel value (99) so GameScreen knows to use it.
"""

import pygame
from game.constants import (
    WINDOW_W, WINDOW_H, GRID_W, GRID_H, BOTTOM_BAR_H,
    GRID_ROWS, GRID_COLS, CELL_W, CELL_H,
    COLORS, AGENT_CONFIGS,
    STATE_GAME, STATE_SELECT_MAP, STATE_TITLE,
)
from game.grid import Grid
from game.agent import Agent
from game.maps import get_map
from game.visualizer import Visualizer


# Toolbar button IDs
_TOOL_WALL   = 'wall'
_TOOL_ERASE  = 'erase'
_TOOL_START  = 'start'
_TOOL_TREAS  = 'treasure'


class EditorScreen:
    """Interactive grid map editor."""

    def __init__(self, surface: pygame.Surface, state_dict: dict):
        self.surface   = surface
        self.state     = state_dict
        self.tick      = 0

        # Start from the currently loaded grid or a blank one
        existing = state_dict.get('grid')
        if existing:
            self.walls    = set(existing.walls)
            self.start    = existing.start
            self.treasure = existing.treasure
        else:
            self.walls    = set()
            self.start    = (GRID_ROWS - 2, 1)
            self.treasure = (1, GRID_COLS - 2)

        # Default border walls
        for c in range(GRID_COLS):
            self.walls.add((0, c))
            self.walls.add((GRID_ROWS - 1, c))
        for r in range(GRID_ROWS):
            self.walls.add((r, 0))
            self.walls.add((r, GRID_COLS - 1))

        self.tool      = _TOOL_WALL
        self._dragging = False
        self._init_fonts()
        self._status   = 'Draw walls with left-click. Right-click to erase.'

        # Live preview visualizer
        self._update_viz()

    # ------------------------------------------------------------------

    def _init_fonts(self):
        def _f(size, bold=False):
            for fam in ('segoe ui', 'arial', 'helvetica', None):
                try:
                    return pygame.font.SysFont(fam, size, bold=bold)
                except Exception:
                    pass
            return pygame.font.Font(None, size)
        self.font_title  = _f(22, bold=True)
        self.font_btn    = _f(14, bold=True)
        self.font_status = _f(14)
        self.font_hint   = _f(13)

    def _update_viz(self):
        g          = Grid(GRID_ROWS, GRID_COLS, self.walls, self.start, self.treasure)
        self._grid = g
        self._viz  = Visualizer(self.surface, g)

    # ------------------------------------------------------------------
    # Screen protocol
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_ESCAPE:
                return STATE_SELECT_MAP
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._save_and_launch()
            if key == pygame.K_c:
                self._clear_interior()
                self._status = 'Cleared. Draw new walls.'
            if key == pygame.K_w:
                self.tool = _TOOL_WALL
                self._status = 'Tool: Wall (left-click drag to place)'
            if key == pygame.K_e:
                self.tool = _TOOL_ERASE
                self._status = 'Tool: Erase (left-click drag to remove)'
            if key == pygame.K_s:
                self.tool = _TOOL_START
                self._status = 'Tool: Start — click to place Start marker'
            if key == pygame.K_t:
                self.tool = _TOOL_TREAS
                self._status = 'Tool: Treasure — click to place Treasure'
            if key == pygame.K_z:
                # Load map 0 as template
                md = get_map(0)
                self.walls    = set(md['walls'])
                self.start    = md['start']
                self.treasure = md['treasure']
                self._update_viz()
                self._status = 'Loaded Simple Open as template.'

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._dragging = True
                self._apply_tool(event.pos, erase=False)
            if event.button == 3:
                self._dragging = True
                self._apply_tool(event.pos, erase=True)

            # Toolbar clicks
            clicked = self._toolbar_click(event.pos)
            if clicked:
                return clicked

        if event.type == pygame.MOUSEBUTTONUP:
            self._dragging = False

        if event.type == pygame.MOUSEMOTION and self._dragging:
            if pygame.mouse.get_pressed()[0]:
                self._apply_tool(event.pos, erase=False)
            elif pygame.mouse.get_pressed()[2]:
                self._apply_tool(event.pos, erase=True)

        return None

    def update(self, dt: float):
        self.tick += 1

    def draw(self):
        surf = self.surface
        surf.fill(COLORS['bg'])

        # Draw the live grid preview
        self._viz.draw([], self.tick, grid=self._grid)

        # Right panel
        self._draw_panel(surf)

        # Bottom bar
        self._draw_bottom_bar(surf)

    # ------------------------------------------------------------------
    # Tool application
    # ------------------------------------------------------------------

    def _pixel_to_cell(self, pos):
        """Convert screen pixel (x,y) to (row, col). Returns None if outside grid."""
        x, y = pos
        if x < 0 or x >= GRID_W or y < 0 or y >= GRID_H:
            return None
        col = x // CELL_W
        row = y // CELL_H
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return (row, col)
        return None

    def _apply_tool(self, pos, erase=False):
        cell = self._pixel_to_cell(pos)
        if cell is None:
            return

        if erase or self.tool == _TOOL_ERASE:
            self.walls.discard(cell)
        elif self.tool == _TOOL_WALL:
            if cell != self.start and cell != self.treasure:
                self.walls.add(cell)
        elif self.tool == _TOOL_START:
            if cell not in self.walls and cell != self.treasure:
                self.start = cell
                self._status = f'Start set to {cell}'
        elif self.tool == _TOOL_TREAS:
            if cell not in self.walls and cell != self.start:
                self.treasure = cell
                self._status = f'Treasure set to {cell}'

        self._update_viz()

    def _clear_interior(self):
        """Remove all non-border walls."""
        border = set()
        for c in range(GRID_COLS):
            border.add((0, c))
            border.add((GRID_ROWS - 1, c))
        for r in range(GRID_ROWS):
            border.add((r, 0))
            border.add((r, GRID_COLS - 1))
        self.walls = border
        self._update_viz()

    # ------------------------------------------------------------------
    # Panel (right side)
    # ------------------------------------------------------------------

    _PANEL_X = GRID_W
    _PANEL_W = WINDOW_W - GRID_W

    def _draw_panel(self, surf):
        px = self._PANEL_X
        pw = self._PANEL_W
        pygame.draw.rect(surf, COLORS['panel_bg'],
                         pygame.Rect(px, 0, pw, WINDOW_H - BOTTOM_BAR_H))
        pygame.draw.line(surf, COLORS['panel_border'],
                         (px, 0), (px, WINDOW_H - BOTTOM_BAR_H), 2)

        cx = px + pw // 2
        y  = 14

        # Title
        ts = self.font_title.render('MAP EDITOR', True, COLORS['text_primary'])
        surf.blit(ts, ts.get_rect(centerx=cx, y=y))
        y += ts.get_height() + 10

        pygame.draw.line(surf, COLORS['panel_border'],
                         (px + 10, y), (px + pw - 10, y), 1)
        y += 12

        # Tool buttons
        tools = [
            (_TOOL_WALL,  '[W] Wall',      COLORS['wall']),
            (_TOOL_ERASE, '[E] Erase',     COLORS['failure']),
            (_TOOL_START, '[S] Set Start', COLORS['start']),
            (_TOOL_TREAS, '[T] Treasure',  COLORS['treasure']),
        ]
        self._tool_rects = {}
        for tool_id, label, color in tools:
            selected = (self.tool == tool_id)
            rect     = pygame.Rect(px + 10, y, pw - 20, 36)
            self._tool_rects[tool_id] = rect
            bg_col   = (*color, 40) if selected else (*COLORS['card_bg'], 255)
            bs       = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            bs.fill(bg_col)
            surf.blit(bs, rect.topleft)
            border_w = 2 if selected else 1
            pygame.draw.rect(surf, color, rect, border_radius=6, width=border_w)
            ls = self.font_btn.render(label, True, color)
            surf.blit(ls, ls.get_rect(center=rect.center))
            y += 44

        y += 6
        pygame.draw.line(surf, COLORS['panel_border'],
                         (px + 10, y), (px + pw - 10, y), 1)
        y += 12

        # [C] Clear button
        clear_rect = pygame.Rect(px + 10, y, pw - 20, 32)
        self._clear_rect = clear_rect
        pygame.draw.rect(surf, COLORS['card_bg'], clear_rect, border_radius=6)
        pygame.draw.rect(surf, COLORS['text_dim'], clear_rect, border_radius=6, width=1)
        cs = self.font_btn.render('[C] Clear Interior', True, COLORS['text_dim'])
        surf.blit(cs, cs.get_rect(center=clear_rect.center))
        y += 42

        # [Z] Load template
        tmpl_rect = pygame.Rect(px + 10, y, pw - 20, 32)
        self._tmpl_rect = tmpl_rect
        pygame.draw.rect(surf, COLORS['card_bg'], tmpl_rect, border_radius=6)
        pygame.draw.rect(surf, COLORS['text_dim'], tmpl_rect, border_radius=6, width=1)
        zs = self.font_btn.render('[Z] Load Template', True, COLORS['text_dim'])
        surf.blit(zs, zs.get_rect(center=tmpl_rect.center))
        y += 50

        pygame.draw.line(surf, COLORS['panel_border'],
                         (px + 10, y), (px + pw - 10, y), 1)
        y += 12

        # Status
        status_surf = self.font_status.render(self._status[:28], True, COLORS['text_secondary'])
        surf.blit(status_surf, (px + 10, y))
        y += status_surf.get_height() + 16

        # Stats
        info_lines = [
            f'Walls : {len(self.walls)}',
            f'Start : {self.start}',
            f'Treas : {self.treasure}',
            f'Rows  : {GRID_ROWS}',
            f'Cols  : {GRID_COLS}',
        ]
        for line in info_lines:
            ls = self.font_hint.render(line, True, COLORS['text_dim'])
            surf.blit(ls, (px + 10, y))
            y += ls.get_height() + 4

        # Launch button
        y = WINDOW_H - BOTTOM_BAR_H - 60
        launch_rect = pygame.Rect(px + 10, y, pw - 20, 44)
        self._launch_rect = launch_rect
        pygame.draw.rect(surf, COLORS['card_bg'], launch_rect, border_radius=8)
        pygame.draw.rect(surf, COLORS['success'], launch_rect, border_radius=8, width=2)
        ls2 = self.font_btn.render('[Enter] Launch Game', True, COLORS['success'])
        surf.blit(ls2, ls2.get_rect(center=launch_rect.center))

    def _draw_bottom_bar(self, surf):
        bar_rect = pygame.Rect(0, GRID_H, GRID_W, BOTTOM_BAR_H)
        pygame.draw.rect(surf, COLORS['panel_bg'], bar_rect)
        pygame.draw.line(surf, COLORS['panel_border'],
                         (0, GRID_H), (GRID_W, GRID_H), 1)

        hints = '[W] Wall  [E] Erase  [S] Start  [T] Treasure  [C] Clear  [Enter] Launch  [Esc] Back'
        hs    = self.font_hint.render(hints, True, COLORS['text_dim'])
        surf.blit(hs, hs.get_rect(centerx=GRID_W // 2,
                                   y=GRID_H + (BOTTOM_BAR_H - hs.get_height()) // 2))

    # ------------------------------------------------------------------
    # Toolbar click handler
    # ------------------------------------------------------------------

    def _toolbar_click(self, pos):
        """Check if pos hits any panel button. Returns state transition or None."""
        for tool_id, rect in getattr(self, '_tool_rects', {}).items():
            if rect.collidepoint(pos):
                self.tool = tool_id
                return None

        if hasattr(self, '_clear_rect') and self._clear_rect.collidepoint(pos):
            self._clear_interior()
            self._status = 'Interior cleared.'
            return None

        if hasattr(self, '_tmpl_rect') and self._tmpl_rect.collidepoint(pos):
            md = get_map(0)
            self.walls    = set(md['walls'])
            self.start    = md['start']
            self.treasure = md['treasure']
            self._update_viz()
            self._status = 'Loaded template.'
            return None

        if hasattr(self, '_launch_rect') and self._launch_rect.collidepoint(pos):
            return self._save_and_launch()

        return None

    # ------------------------------------------------------------------

    def _save_and_launch(self):
        """Save the custom grid into state and transition to the game."""
        g = Grid(GRID_ROWS, GRID_COLS, self.walls, self.start, self.treasure)
        self.state['custom_grid'] = g
        self.state['grid']        = g
        self.state['map_idx']     = 99  # sentinel for custom map

        # Rebuild fresh agents
        agents = []
        for i, cfg in enumerate(AGENT_CONFIGS):
            a        = Agent(cfg['name'], cfg['algo_key'], cfg['color'])
            a.active = self.state['active_agents'][i]
            agents.append(a)
        self.state['agents']          = agents
        self.state['winner_first']    = ''
        self.state['winner_shortest'] = ''
        self.state['paused']          = False

        return STATE_GAME
