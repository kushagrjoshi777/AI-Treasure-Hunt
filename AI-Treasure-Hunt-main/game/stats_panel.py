"""Stats Panel — right-side HUD for the AI Treasure Hunt.

Layout (top to bottom):
  +------------------------------+
  |     AI Treasure Hunt         |  <- title
  +------------------------------+
  | [Agent card] x 4             |  <- one per agent, left color border
  +------------------------------+
  |  Speed: [- 4x +]             |  <- speed control
  +------------------------------+
  |  Controls                    |  <- key binding legend
  +------------------------------+
"""

import math
import time
import pygame
from game.constants import (
    COLORS, GRID_W, WINDOW_W, WINDOW_H, BOTTOM_BAR_H, PANEL_W, SPEEDS,
)

PANEL_X    = GRID_W
PANEL_H    = WINDOW_H - BOTTOM_BAR_H
PANEL_RECT = pygame.Rect(PANEL_X, 0, PANEL_W, PANEL_H)

CARD_MARGIN = 10
CARD_W      = PANEL_W - CARD_MARGIN * 2
CARD_H      = 110
CARD_X      = PANEL_X + CARD_MARGIN
CARDS_TOP   = 50
CARD_GAP    = 6

STATUS_COLOR = {
    'idle':      COLORS['text_dim'],
    'searching': COLORS['dfs'],
    'found':     COLORS['success'],
    'failed':    COLORS['failure'],
}


class StatsPanel:

    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self._init_fonts()

    def _init_fonts(self):
        def font(size, bold=False):
            for family in ('segoe ui', 'arial', 'helvetica', None):
                try:
                    return pygame.font.SysFont(family, size, bold=bold)
                except Exception:
                    continue
            return pygame.font.Font(None, size)

        self.font_title      = font(18, bold=True)
        self.font_agent_name = font(16, bold=True)
        self.font_stat_label = font(13)
        self.font_stat_value = font(13, bold=True)
        self.font_speed      = font(14, bold=True)
        self.font_controls   = font(12)
        self.font_winner     = font(12, bold=True)
        self.font_pause      = font(15, bold=True)
        self.font_badge      = font(11, bold=True)

    def draw(self, agents: list, tick: int, speed_idx: int, paused: bool):
        surf = self.surface

        # Background
        pygame.draw.rect(surf, COLORS['panel_bg'], PANEL_RECT)

        # Title
        self._draw_title(surf)

        # Agent cards
        for i, agent in enumerate(agents):
            card_y = CARDS_TOP + i * (CARD_H + CARD_GAP)
            self._draw_agent_card(surf, agent, CARD_X, card_y, tick)

        # Speed + pause
        indicator_y = CARDS_TOP + 4 * (CARD_H + CARD_GAP) + 10
        self._draw_speed_indicator(surf, speed_idx, indicator_y)
        pause_y = indicator_y + 38
        if paused:
            self._draw_pause_badge(surf, pause_y, tick)

        # Controls legend
        controls_y = pause_y + (40 if paused else 4)
        self._draw_controls(surf, controls_y)

        # Panel left border
        pygame.draw.line(surf, COLORS['panel_border'],
                         (PANEL_X, 0), (PANEL_X, PANEL_H), 1)

    def _draw_title(self, surf):
        text = 'AI Treasure Hunt'
        title_surf = self.font_title.render(text, True, COLORS['text_primary'])
        title_rect = title_surf.get_rect(x=PANEL_X + CARD_MARGIN, y=14)
        surf.blit(title_surf, title_rect)
        # Underline
        line_y = title_rect.bottom + 6
        pygame.draw.line(surf, COLORS['panel_border'],
                         (PANEL_X + CARD_MARGIN, line_y),
                         (PANEL_X + PANEL_W - CARD_MARGIN, line_y), 1)

    def _draw_agent_card(self, surf, agent, x, y, tick):
        card_rect = pygame.Rect(x, y, CARD_W, CARD_H)

        # Card background
        pygame.draw.rect(surf, COLORS['card_bg'], card_rect, border_radius=6)

        # Winner border
        if agent.first_found and agent.status == 'found':
            pulse = (math.sin(tick * 0.12) + 1) / 2
            border_alpha = int(160 + 90 * pulse)
            border_surf = pygame.Surface((CARD_W + 4, CARD_H + 4), pygame.SRCALPHA)
            pygame.draw.rect(border_surf, (*COLORS['success'], border_alpha),
                             pygame.Rect(0, 0, CARD_W + 4, CARD_H + 4),
                             border_radius=7, width=2)
            surf.blit(border_surf, (x - 2, y - 2))
        else:
            pygame.draw.rect(surf, COLORS['panel_border'], card_rect,
                             border_radius=6, width=1)

        # Left color accent bar
        accent_color = agent.color if agent.active else COLORS['text_dim']
        pygame.draw.rect(surf, accent_color,
                         pygame.Rect(x, y + 4, 4, CARD_H - 8),
                         border_radius=2)

        inner_x = x + 14
        inner_y = y + 8

        # Agent name in agent's color
        name_color = agent.color if agent.active else COLORS['text_dim']
        name_surf = self.font_agent_name.render(agent.name, True, name_color)
        surf.blit(name_surf, (inner_x, inner_y))

        stat_y = inner_y + name_surf.get_height() + 6

        # Stats: label left, value right
        stats = [
            ('Explored', str(agent.nodes_explored)),
            ('Path',
             str(agent.path_length) if agent.status == 'found' else '--'),
            ('Time', agent.time_text),
            ('Status', agent.status_text),
        ]

        for label, value in stats:
            # Status gets special color
            if label == 'Status':
                vc = STATUS_COLOR.get(agent.status, COLORS['text_secondary'])
                if not agent.active:
                    vc = COLORS['text_dim']
            else:
                vc = COLORS['text_primary']

            label_surf = self.font_stat_label.render(label, True, COLORS['text_secondary'])
            value_surf = self.font_stat_value.render(value, True, vc)

            surf.blit(label_surf, (inner_x, stat_y))
            value_rect = value_surf.get_rect(right=x + CARD_W - 10, y=stat_y)
            surf.blit(value_surf, value_rect)
            stat_y += max(label_surf.get_height(), value_surf.get_height()) + 2

        # Winner badge
        if agent.first_found and agent.status == 'found':
            pulse_t = (math.sin(tick * 0.15) + 1) / 2
            gold = (int(220 + 35 * pulse_t), int(180 + 35 * pulse_t), 0)
            badge = self.font_winner.render('WINNER', True, gold)
            surf.blit(badge, (x + CARD_W - badge.get_width() - 10, y + 8))

        # Inactive overlay
        if not agent.active:
            overlay = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            surf.blit(overlay, (x, y))
            inactive_surf = self.font_badge.render('INACTIVE', True, COLORS['text_dim'])
            surf.blit(inactive_surf,
                      inactive_surf.get_rect(centerx=x + CARD_W // 2,
                                             centery=y + CARD_H // 2))

    def _draw_speed_indicator(self, surf, speed_idx, y):
        cx = PANEL_X + PANEL_W // 2
        speed = SPEEDS[speed_idx]

        pygame.draw.line(surf, COLORS['panel_border'],
                         (PANEL_X + CARD_MARGIN, y),
                         (PANEL_X + PANEL_W - CARD_MARGIN, y), 1)
        y += 8

        left = self.font_speed.render('[-]', True, COLORS['text_dim'])
        right = self.font_speed.render('[+]', True, COLORS['text_dim'])
        speed_surf = self.font_speed.render(f'Speed: {speed}x', True, COLORS['text_primary'])

        speed_rect = speed_surf.get_rect(centerx=cx, y=y)
        surf.blit(left, (PANEL_X + CARD_MARGIN, y))
        surf.blit(speed_surf, speed_rect)
        surf.blit(right, (PANEL_X + PANEL_W - CARD_MARGIN - right.get_width(), y))

    def _draw_pause_badge(self, surf, y, tick):
        if time.time() % 1.0 < 0.5:
            cx = PANEL_X + PANEL_W // 2
            pause_surf = self.font_pause.render('PAUSED', True, COLORS['failure'])
            pause_rect = pause_surf.get_rect(centerx=cx, y=y)
            surf.blit(pause_surf, pause_rect)

    def _draw_controls(self, surf, y):
        cx = PANEL_X + PANEL_W // 2

        pygame.draw.line(surf, COLORS['panel_border'],
                         (PANEL_X + CARD_MARGIN, y),
                         (PANEL_X + PANEL_W - CARD_MARGIN, y), 1)
        y += 8

        bindings = [
            ('[SPACE]', 'Pause'),
            ('[R]',     'Restart'),
            ('[N]',     'New Map'),
            ('[+/-]',   'Speed'),
            ('[1-4]',   'Toggle Agent'),
            ('[E]',     'Editor'),
            ('[ESC]',   'Menu'),
        ]

        lx = PANEL_X + CARD_MARGIN
        rx = PANEL_X + PANEL_W - CARD_MARGIN

        for key, action in bindings:
            key_surf = self.font_controls.render(key, True, COLORS['text_secondary'])
            action_surf = self.font_controls.render(action, True, COLORS['text_dim'])
            surf.blit(key_surf, (lx, y))
            surf.blit(action_surf, action_surf.get_rect(right=rx, y=y))
            y += key_surf.get_height() + 2
