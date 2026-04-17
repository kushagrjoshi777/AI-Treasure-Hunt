"""
Results Screen — displayed after all agents finish searching.

Shows a comprehensive comparison of all agents:
  - Winner banner with crown
  - Data table: Nodes Explored | Path Length | Time | Status
  - Two bar charts: Nodes Explored & Path Length
  - Algorithm property comparison grid (Complete / Optimal / Time / Space)
  - Navigation hints

Transitions:
  R / ENTER → restart same map (STATE_GAME)
  N         → new random map  (STATE_GAME with map_idx=3)
  S         → select map      (STATE_SELECT_MAP)
  ESC       → title           (STATE_TITLE)
"""

import math
import pygame
from game.constants import (
    WINDOW_W, WINDOW_H, COLORS, AGENT_CONFIGS,
    STATE_TITLE, STATE_SELECT_MAP, STATE_GAME,
    GRID_ROWS, GRID_COLS, MAP_NAMES,
)
from game.agent import Agent
from game.grid import Grid
from game.maps import get_map


# ── Algorithm property table ──────────────────────────────────────────────────
_ALGO_PROPS = {
    'bfs'   : {'complete': 'Yes', 'optimal': 'Yes', 'time': 'O(b^d)', 'space': 'O(b^d)'},
    'dfs'   : {'complete': 'No',  'optimal': 'No',  'time': 'O(b^m)', 'space': 'O(bm)'},
    'astar' : {'complete': 'Yes', 'optimal': 'Yes', 'time': 'O(b^d)', 'space': 'O(b^d)'},
    'greedy': {'complete': 'No',  'optimal': 'No',  'time': 'O(b^m)', 'space': 'O(b^m)'},
}


class ResultsScreen:
    """Post-race results and comparison screen."""

    def __init__(self, surface: pygame.Surface, state_dict: dict):
        self.surface = surface
        self.state   = state_dict
        self.tick    = 0
        self._init_fonts()
        self._bar_anim = 0.0   # 0.0 → 1.0 over ~60 frames

    # ------------------------------------------------------------------

    def _init_fonts(self):
        def _f(size, bold=False):
            for fam in ('segoe ui', 'arial', 'helvetica', None):
                try:
                    return pygame.font.SysFont(fam, size, bold=bold)
                except Exception:
                    pass
            return pygame.font.Font(None, size)

        self.font_title   = _f(32, bold=True)
        self.font_winner  = _f(22, bold=True)
        self.font_header  = _f(14, bold=True)
        self.font_cell    = _f(14)
        self.font_hint    = _f(14)
        self.font_prop_h  = _f(13, bold=True)
        self.font_prop    = _f(13)

    # ------------------------------------------------------------------
    # Screen protocol
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_ESCAPE:
                return STATE_TITLE
            if key in (pygame.K_s,):
                return STATE_SELECT_MAP
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_r):
                return self._restart_same()
            if key == pygame.K_n:
                return self._restart_new()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self._btn_again_rect().collidepoint(mx, my):
                return self._restart_same()
            if self._btn_select_rect().collidepoint(mx, my):
                return STATE_SELECT_MAP
            if self._btn_menu_rect().collidepoint(mx, my):
                return STATE_TITLE
        return None

    def update(self, dt: float):
        self.tick       += 1
        self._bar_anim   = min(1.0, self._bar_anim + 0.025)

    def draw(self):
        surf = self.surface
        surf.fill(COLORS['bg'])

        self._draw_title(surf)
        self._draw_winner_banner(surf)
        self._draw_data_table(surf)
        self._draw_bar_charts(surf)
        self._draw_algo_props(surf)
        self._draw_buttons(surf)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _agents(self):
        return self.state.get('agents', [])

    def _restart_same(self):
        map_idx  = self.state.get('map_idx', 0)
        map_data = get_map(map_idx)
        self.state['grid'] = Grid(GRID_ROWS, GRID_COLS,
                                  map_data['walls'],
                                  map_data['start'],
                                  map_data['treasure'])
        self._rebuild_agents()
        return STATE_GAME

    def _restart_new(self):
        self.state['map_idx'] = 3
        map_data = get_map(3)
        self.state['grid'] = Grid(GRID_ROWS, GRID_COLS,
                                  map_data['walls'],
                                  map_data['start'],
                                  map_data['treasure'])
        self._rebuild_agents()
        return STATE_GAME

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

    # ------------------------------------------------------------------
    # Button rects
    # ------------------------------------------------------------------

    def _btn_again_rect(self):
        return pygame.Rect(WINDOW_W // 2 - 280, WINDOW_H - 60, 160, 40)

    def _btn_select_rect(self):
        return pygame.Rect(WINDOW_W // 2 - 80, WINDOW_H - 60, 160, 40)

    def _btn_menu_rect(self):
        return pygame.Rect(WINDOW_W // 2 + 120, WINDOW_H - 60, 160, 40)

    # ------------------------------------------------------------------
    # Draw sections
    # ------------------------------------------------------------------

    def _draw_title(self, surf):
        text = 'RACE  RESULTS'
        ts   = self.font_title.render(text, True, COLORS['text_primary'])
        surf.blit(ts, ts.get_rect(centerx=WINDOW_W // 2, y=14))

        # Map name tag
        idx      = self.state.get('map_idx', 0)
        map_name = MAP_NAMES[min(idx, len(MAP_NAMES) - 1)]
        ms       = self.font_hint.render(f'Map: {map_name}', True, COLORS['text_dim'])
        surf.blit(ms, ms.get_rect(centerx=WINDOW_W // 2, y=54))

        pygame.draw.line(surf, COLORS['panel_border'],
                         (30, 76), (WINDOW_W - 30, 76), 1)

    def _draw_winner_banner(self, surf):
        wf  = self.state.get('winner_first', '')
        ws  = self.state.get('winner_shortest', '')
        y   = 86
        cx  = WINDOW_W // 2

        pulse = (math.sin(self.tick * 0.1) + 1) / 2
        gold  = (int(200 + 55 * pulse), int(170 + 45 * pulse), 0)

        if wf:
            t = f'  First to Finish:  {wf}   '
            ts = self.font_winner.render(t, True, gold)
            surf.blit(ts, ts.get_rect(centerx=cx, y=y))
            y += 30

        if ws and ws != wf:
            t  = f'  Shortest Path:  {ws}   '
            ts2 = self.font_winner.render(t, True, COLORS['astar'])
            surf.blit(ts2, ts2.get_rect(centerx=cx, y=y))
            y += 30
        elif ws == wf and wf:
            note = self.font_hint.render('(same agent — optimal AND fastest!)',
                                         True, COLORS['success'])
            surf.blit(note, note.get_rect(centerx=cx, y=y))

    def _draw_data_table(self, surf):
        """Draw a table: Agent | Nodes | Path Len | Time | Status."""
        TABLE_X  = 30
        TABLE_Y  = 160
        ROW_H    = 32
        COL_WS   = [120, 140, 120, 130, 140]   # widths per column
        HEADERS  = ['Agent', 'Nodes Explored', 'Path Length', 'Time', 'Status']

        # Header row
        x = TABLE_X
        for w, h in zip(COL_WS, HEADERS):
            hs = self.font_header.render(h, True, COLORS['text_secondary'])
            surf.blit(hs, (x + 4, TABLE_Y))
            x += w
        pygame.draw.line(surf, COLORS['panel_border'],
                         (TABLE_X, TABLE_Y + ROW_H - 4),
                         (TABLE_X + sum(COL_WS), TABLE_Y + ROW_H - 4), 1)

        for row_i, agent in enumerate(self._agents()):
            ry = TABLE_Y + ROW_H + row_i * ROW_H

            # Row background
            row_color = (*agent.color, 20) if agent.active else (30, 30, 50, 255)
            rs = pygame.Surface((sum(COL_WS), ROW_H - 2), pygame.SRCALPHA)
            rs.fill((*agent.color, 18) if agent.active else (30, 30, 50, 100))
            surf.blit(rs, (TABLE_X, ry))

            # Left accent bar
            pygame.draw.rect(surf, agent.color if agent.active else COLORS['text_dim'],
                             pygame.Rect(TABLE_X, ry, 4, ROW_H - 2))

            values = [
                agent.name,
                str(agent.nodes_explored) if agent.active else '--',
                str(agent.path_length) if (agent.active and agent.status == 'found') else '--',
                agent.time_text if agent.active else '--',
                agent.status_text if agent.active else 'Inactive',
            ]
            status_colors = {
                'found':  COLORS['success'],
                'failed': COLORS['failure'],
            }
            cell_colors = [
                agent.color if agent.active else COLORS['text_dim'],
                COLORS['text_primary'],
                COLORS['text_primary'],
                COLORS['text_primary'],
                status_colors.get(agent.status, COLORS['text_secondary']),
            ]

            x = TABLE_X
            for ci, (w, val, cc) in enumerate(zip(COL_WS, values, cell_colors)):
                vs = self.font_cell.render(val, True, cc)
                surf.blit(vs, (x + 6, ry + (ROW_H - vs.get_height()) // 2))
                x += w

        table_bottom = TABLE_Y + ROW_H * (len(self._agents()) + 1)
        pygame.draw.line(surf, COLORS['panel_border'],
                         (TABLE_X, table_bottom),
                         (TABLE_X + sum(COL_WS), table_bottom), 1)

    def _draw_bar_charts(self, surf):
        """Draw two bar charts: Nodes Explored and Path Length."""
        agents  = [a for a in self._agents() if a.active]
        if not agents:
            return

        # Chart area: right column
        CHART_X  = 680
        CHART_Y  = 160
        CHART_W  = 320
        CHART_H  = 180
        GAP      = 30

        self._draw_single_bar_chart(
            surf, agents,
            [a.nodes_explored for a in agents],
            'Nodes Explored',
            CHART_X, CHART_Y, CHART_W, CHART_H,
        )
        self._draw_single_bar_chart(
            surf, agents,
            [a.path_length for a in agents],
            'Path Length',
            CHART_X, CHART_Y + CHART_H + GAP, CHART_W, CHART_H,
        )

    def _draw_single_bar_chart(self, surf, agents, values, title,
                               x, y, w, h):
        # Background
        pygame.draw.rect(surf, COLORS['card_bg'],
                         pygame.Rect(x, y, w, h), border_radius=6)
        pygame.draw.rect(surf, COLORS['panel_border'],
                         pygame.Rect(x, y, w, h), border_radius=6, width=1)

        # Title
        ts = self.font_header.render(title, True, COLORS['text_secondary'])
        surf.blit(ts, (x + 8, y + 6))

        max_val  = max(values) if any(v > 0 for v in values) else 1
        bar_area_y  = y + 28
        bar_area_h  = h - 50
        bar_area_w  = w - 20
        n        = len(agents)
        bar_w    = max(8, (bar_area_w - (n - 1) * 6) // n)

        for i, (agent, val) in enumerate(zip(agents, values)):
            bar_h  = int((val / max_val) * bar_area_h * self._bar_anim)
            bx     = x + 10 + i * (bar_w + 6)
            by     = bar_area_y + bar_area_h - bar_h
            pygame.draw.rect(surf, agent.color,
                             pygame.Rect(bx, by, bar_w, bar_h),
                             border_radius=3)

            # Value label above bar
            vl = self.font_prop.render(str(val), True, agent.color)
            surf.blit(vl, (bx + bar_w // 2 - vl.get_width() // 2,
                            by - vl.get_height() - 2))

            # Agent name label below
            nl = self.font_prop.render(agent.name, True, COLORS['text_dim'])
            surf.blit(nl, (bx + bar_w // 2 - nl.get_width() // 2,
                            bar_area_y + bar_area_h + 4))

    def _draw_algo_props(self, surf):
        """Draw algorithm properties table (Complete / Optimal / Time / Space)."""
        TABLE_X  = 30
        TABLE_Y  = 370
        ROW_H    = 28
        COL_WS   = [120, 90, 90, 110, 110]
        HEADERS  = ['Algorithm', 'Complete', 'Optimal', 'Time', 'Space']

        pygame.draw.line(surf, COLORS['panel_border'],
                         (TABLE_X, TABLE_Y - 4),
                         (TABLE_X + sum(COL_WS), TABLE_Y - 4), 1)

        sec_label = self.font_header.render('ALGORITHM PROPERTIES (CO2)',
                                            True, COLORS['text_dim'])
        surf.blit(sec_label, (TABLE_X, TABLE_Y - 22))

        x = TABLE_X
        for w, h in zip(COL_WS, HEADERS):
            hs = self.font_prop_h.render(h, True, COLORS['text_secondary'])
            surf.blit(hs, (x + 4, TABLE_Y))
            x += w

        pygame.draw.line(surf, COLORS['panel_border'],
                         (TABLE_X, TABLE_Y + ROW_H - 4),
                         (TABLE_X + sum(COL_WS), TABLE_Y + ROW_H - 4), 1)

        for ri, cfg in enumerate(AGENT_CONFIGS):
            ry    = TABLE_Y + ROW_H + ri * ROW_H
            props = _ALGO_PROPS[cfg['algo_key']]
            color = cfg['color']

            rs = pygame.Surface((sum(COL_WS), ROW_H - 2), pygame.SRCALPHA)
            rs.fill((*color, 15))
            surf.blit(rs, (TABLE_X, ry))
            pygame.draw.rect(surf, color, pygame.Rect(TABLE_X, ry, 4, ROW_H - 2))

            values = [
                cfg['name'],
                props['complete'],
                props['optimal'],
                props['time'],
                props['space'],
            ]
            vcols  = [
                color,
                COLORS['success'] if props['complete'] == 'Yes' else COLORS['failure'],
                COLORS['success'] if props['optimal']  == 'Yes' else COLORS['failure'],
                COLORS['text_secondary'],
                COLORS['text_secondary'],
            ]

            x = TABLE_X
            for w, v, vc in zip(COL_WS, values, vcols):
                vs = self.font_prop.render(v, True, vc)
                surf.blit(vs, (x + 6, ry + (ROW_H - vs.get_height()) // 2))
                x += w

    def _draw_buttons(self, surf):
        buttons = [
            (self._btn_again_rect(),  '[R] Play Again',    COLORS['success']),
            (self._btn_select_rect(), '[S] Select Map',    COLORS['highlight']),
            (self._btn_menu_rect(),   '[Esc] Main Menu',   COLORS['text_secondary']),
        ]
        mx, my = pygame.mouse.get_pos()
        for rect, label, color in buttons:
            hovered = rect.collidepoint(mx, my)
            bg      = (*color, 40) if hovered else (*COLORS['card_bg'], 255)
            bs      = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            bs.fill(bg)
            surf.blit(bs, rect.topleft)
            pygame.draw.rect(surf, color, rect, border_radius=6, width=2 if hovered else 1)
            ls = self.font_hint.render(label, True, color)
            surf.blit(ls, ls.get_rect(center=rect.center))
