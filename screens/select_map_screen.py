"""
Select Map Screen — lets the player choose one of four pre-built maps
(or a custom map from the editor) before starting the race.

Layout:
  - Title bar: "SELECT MAP"
  - 4 large map preview cards in a 2×2 grid
  - "Custom Map" card if state_dict['custom_grid'] is not None
  - Agent toggle checkboxes at the bottom
  - [Enter] Start  [ESC] Back  [E] Editor

Transitions:
  ENTER / card click → STATE_GAME
  ESC               → STATE_TITLE
  E                 → STATE_EDITOR
"""

import math
import pygame
from game.constants import (
    WINDOW_W, WINDOW_H, COLORS, AGENT_CONFIGS,
    MAP_NAMES, STATE_GAME, STATE_TITLE, STATE_EDITOR,
    GRID_ROWS, GRID_COLS,
)
from game.maps import get_map
from game.grid import Grid
from game.agent import Agent


# ── Card layout ──────────────────────────────────────────────────────────────
_CARD_COLS   = 2
_CARD_ROWS   = 2
_MARGIN      = 40
_HEADER_H    = 100
_FOOTER_H    = 140
_CARD_GAP    = 20
_CARD_W      = (WINDOW_W - _MARGIN * 2 - _CARD_GAP * (_CARD_COLS - 1)) // _CARD_COLS
_CARD_H      = (WINDOW_H - _HEADER_H - _FOOTER_H - _MARGIN - _CARD_GAP * (_CARD_ROWS - 1)) // _CARD_ROWS


class SelectMapScreen:
    """Map selection screen with animated preview thumbnails."""

    def __init__(self, surface: pygame.Surface, state_dict: dict):
        self.surface  = surface
        self.state    = state_dict
        self.tick     = 0
        self.selected = state_dict.get('map_idx', 0)
        self._cards   = self._build_cards()
        self._init_fonts()

    # ------------------------------------------------------------------

    def _init_fonts(self):
        def _f(size, bold=False):
            for fam in ('segoe ui', 'arial', 'helvetica', None):
                try:
                    return pygame.font.SysFont(fam, size, bold=bold)
                except Exception:
                    pass
            return pygame.font.Font(None, size)

        self.font_title  = _f(36, bold=True)
        self.font_card   = _f(18, bold=True)
        self.font_sub    = _f(13)
        self.font_hint   = _f(15)
        self.font_toggle = _f(16, bold=True)
        self.font_label  = _f(13)

    def _build_cards(self):
        """Pre-render mini thumbnails for each map."""
        cards = []
        for i, name in enumerate(MAP_NAMES):
            map_data = get_map(i)
            cards.append({
                'idx'      : i,
                'name'     : name,
                'map_data' : map_data,
                'thumb'    : self._render_thumb(map_data),
            })
        return cards

    def _render_thumb(self, map_data: dict) -> pygame.Surface:
        """Draw a tiny grid preview (walls, start, treasure) into a Surface."""
        TH = 90   # thumbnail height
        TW = int(TH * GRID_COLS / GRID_ROWS)
        surf = pygame.Surface((TW, TH))
        surf.fill(COLORS['bg'])

        cw = max(1, TW // GRID_COLS)
        ch = max(1, TH // GRID_ROWS)

        for (r, c) in map_data['walls']:
            pygame.draw.rect(surf, COLORS['wall'],
                             pygame.Rect(c * cw, r * ch, cw, ch))

        sr, sc = map_data['start']
        pygame.draw.rect(surf, COLORS['start'],
                         pygame.Rect(sc * cw, sr * ch, max(cw, 3), max(ch, 3)))

        tr, tc = map_data['treasure']
        pygame.draw.rect(surf, COLORS['treasure'],
                         pygame.Rect(tc * cw, tr * ch, max(cw, 3), max(ch, 3)))

        return surf

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    def _card_rect(self, idx: int) -> pygame.Rect:
        row = idx // _CARD_COLS
        col = idx  % _CARD_COLS
        x   = _MARGIN + col * (_CARD_W + _CARD_GAP)
        y   = _HEADER_H + row * (_CARD_H + _CARD_GAP)
        return pygame.Rect(x, y, _CARD_W, _CARD_H)

    def _agent_toggle_rect(self, agent_idx: int) -> pygame.Rect:
        total_w   = len(AGENT_CONFIGS) * 160
        start_x   = (WINDOW_W - total_w) // 2
        y         = WINDOW_H - _FOOTER_H + 20
        x         = start_x + agent_idx * 160
        return pygame.Rect(x, y, 150, 50)

    # ------------------------------------------------------------------
    # Screen protocol
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return self._launch_game()
            if key == pygame.K_ESCAPE:
                return STATE_TITLE
            if key == pygame.K_e:
                return STATE_EDITOR
            if key == pygame.K_LEFT:
                self.selected = (self.selected - 1) % len(self._cards)
            if key == pygame.K_RIGHT:
                self.selected = (self.selected + 1) % len(self._cards)
            if key == pygame.K_UP:
                self.selected = (self.selected - _CARD_COLS) % len(self._cards)
            if key == pygame.K_DOWN:
                self.selected = (self.selected + _CARD_COLS) % len(self._cards)
            # Number keys 1-4 select map
            if pygame.K_1 <= key <= pygame.K_4:
                self.selected = key - pygame.K_1
            # Agent toggles via F-keys would be too complex here; use mouse

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Check card clicks
            for card in self._cards:
                r = self._card_rect(card['idx'])
                if r.collidepoint(mx, my):
                    self.selected = card['idx']
                    # Double-click / second click launches immediately
                    return self._launch_game()
            # Agent toggle buttons
            for i in range(len(AGENT_CONFIGS)):
                tr = self._agent_toggle_rect(i)
                if tr.collidepoint(mx, my):
                    self.state['active_agents'][i] = not self.state['active_agents'][i]

        return None

    def update(self, dt: float):
        self.tick += 1

    def draw(self):
        surf = self.surface
        surf.fill(COLORS['bg'])

        self._draw_header(surf)
        self._draw_cards(surf)
        self._draw_agent_toggles(surf)
        self._draw_footer_hints(surf)

    # ------------------------------------------------------------------
    # Draw helpers
    # ------------------------------------------------------------------

    def _draw_header(self, surf):
        cx   = WINDOW_W // 2
        text = 'SELECT  MAP'
        ts   = self.font_title.render(text, True, COLORS['text_primary'])
        surf.blit(ts, ts.get_rect(centerx=cx, y=18))

        sub  = 'Arrow keys / click to choose — Enter to start'
        ss   = self.font_sub.render(sub, True, COLORS['text_dim'])
        surf.blit(ss, ss.get_rect(centerx=cx, y=62))

        # Bottom border
        pygame.draw.line(surf, COLORS['panel_border'],
                         (_MARGIN, _HEADER_H - 8),
                         (WINDOW_W - _MARGIN, _HEADER_H - 8), 1)

    def _draw_cards(self, surf):
        for card in self._cards:
            idx  = card['idx']
            rect = self._card_rect(idx)
            sel  = (idx == self.selected)
            self._draw_card(surf, card, rect, sel)

    def _draw_card(self, surf, card, rect, selected):
        color = AGENT_CONFIGS[card['idx'] % len(AGENT_CONFIGS)]['color']

        # Background
        bg_color = COLORS['card_bg']
        pygame.draw.rect(surf, bg_color, rect, border_radius=10)

        # Border: glowing if selected
        if selected:
            pulse = (math.sin(self.tick * 0.1) + 1) / 2
            bc    = tuple(min(255, int(c + 60 * pulse)) for c in color)
            pygame.draw.rect(surf, bc, rect, border_radius=10, width=3)
        else:
            pygame.draw.rect(surf, COLORS['panel_border'], rect, border_radius=10, width=1)

        # Coloured top bar
        top_bar = pygame.Rect(rect.x, rect.y, rect.width, 6)
        pygame.draw.rect(surf, color, top_bar,
                         border_radius=10)

        # Map name
        name_surf = self.font_card.render(card['name'], True,
                                          color if selected else COLORS['text_primary'])
        surf.blit(name_surf, (rect.x + 12, rect.y + 14))

        # Thumbnail centred in the card
        thumb     = card['thumb']
        tw, th    = thumb.get_size()
        tx        = rect.centerx - tw // 2
        ty        = rect.y + 42
        # Scale up the thumb to fill available space
        avail_w   = rect.width  - 24
        avail_h   = rect.height - 60
        scale     = min(avail_w / max(tw, 1), avail_h / max(th, 1))
        new_w     = int(tw * scale)
        new_h     = int(th * scale)
        scaled    = pygame.transform.scale(thumb, (new_w, new_h))
        tx        = rect.centerx - new_w // 2
        ty        = rect.y + 42
        surf.blit(scaled, (tx, ty))

        # "SELECTED" badge
        if selected:
            badge = self.font_label.render('SELECTED', True, color)
            br    = badge.get_rect(right=rect.right - 10, bottom=rect.bottom - 8)
            surf.blit(badge, br)

    def _draw_agent_toggles(self, surf):
        """Draw on/off toggle buttons for each agent."""
        y_label = WINDOW_H - _FOOTER_H + 4
        cx      = WINDOW_W // 2
        lbl     = self.font_label.render('Toggle Agents (click):', True, COLORS['text_dim'])
        surf.blit(lbl, lbl.get_rect(centerx=cx, y=y_label))

        for i, cfg in enumerate(AGENT_CONFIGS):
            rect   = self._agent_toggle_rect(i)
            active = self.state['active_agents'][i]
            color  = cfg['color'] if active else COLORS['text_dim']
            bg     = COLORS['card_bg']
            pygame.draw.rect(surf, bg, rect, border_radius=8)
            pygame.draw.rect(surf, color, rect, border_radius=8, width=2)

            name_s = self.font_toggle.render(cfg['name'], True, color)
            surf.blit(name_s, name_s.get_rect(center=rect.center))

            if not active:
                # Strikethrough overlay
                mid_y = rect.centery
                pygame.draw.line(surf, COLORS['failure'],
                                 (rect.x + 8, mid_y), (rect.right - 8, mid_y), 2)

    def _draw_footer_hints(self, surf):
        hints = '[Enter] Start    [Arrow keys] Navigate    [E] Editor    [Esc] Back'
        hs    = self.font_hint.render(hints, True, COLORS['text_dim'])
        surf.blit(hs, hs.get_rect(centerx=WINDOW_W // 2, y=WINDOW_H - 28))

    # ------------------------------------------------------------------

    def _launch_game(self):
        """Update shared state and transition to game screen."""
        self.state['map_idx'] = self.selected
        map_data = get_map(self.selected)

        # Use custom grid if editor produced one and selected > standard maps
        if self.state.get('custom_grid') is not None and self.selected >= len(MAP_NAMES):
            grid = self.state['custom_grid']
        else:
            grid = Grid(GRID_ROWS, GRID_COLS,
                        map_data['walls'], map_data['start'], map_data['treasure'])

        self.state['grid'] = grid

        # Rebuild agents respecting active toggles
        agents = []
        for i, cfg in enumerate(AGENT_CONFIGS):
            a        = Agent(cfg['name'], cfg['algo_key'], cfg['color'])
            a.active = self.state['active_agents'][i]
            agents.append(a)
        self.state['agents']         = agents
        self.state['winner_first']   = ''
        self.state['winner_shortest'] = ''
        self.state['paused']         = False

        return STATE_GAME
