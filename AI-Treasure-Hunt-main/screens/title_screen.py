"""Title Screen — clean, minimal with subtle floating particles."""

import math
import random
import pygame
from game.constants import (
    WINDOW_W, WINDOW_H, COLORS,
    STATE_SELECT_MAP, STATE_EDITOR, STATE_QUIT, AGENT_CONFIGS,
)


class _Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'radius', 'alpha', 'color', 'life', 'max_life')

    def __init__(self, rng):
        self.reset(rng, spawn=True)

    def reset(self, rng, spawn=False):
        self.x        = rng.uniform(0, WINDOW_W)
        self.y        = rng.uniform(0, WINDOW_H) if spawn else float(WINDOW_H + 10)
        self.vx       = rng.uniform(-0.2, 0.2)
        self.vy       = rng.uniform(-0.4, -0.1)
        self.radius   = rng.uniform(1.0, 2.0)
        self.max_life = rng.uniform(150, 400)
        self.life     = rng.uniform(0, self.max_life) if spawn else self.max_life
        idx           = rng.randint(0, len(AGENT_CONFIGS) - 1)
        self.color    = AGENT_CONFIGS[idx]['color']
        self.alpha    = 0

    def update(self, rng):
        self.x    += self.vx
        self.y    += self.vy
        self.life -= 1
        t          = self.life / self.max_life
        self.alpha = int(120 * math.sin(t * math.pi))
        if self.life <= 0 or self.y < -10:
            self.reset(rng)


class TitleScreen:

    NUM_PARTICLES = 50

    def __init__(self, surface, state_dict):
        self.surface    = surface
        self.state      = state_dict
        self.tick       = 0
        self._rng       = random.Random()
        self._particles = [_Particle(self._rng) for _ in range(self.NUM_PARTICLES)]
        self._init_fonts()
        self._algo_names = [cfg['name'] + ' -- ' + _ALGO_DESC[cfg['algo_key']]
                            for cfg in AGENT_CONFIGS]
        self._algo_idx   = 0
        self._algo_timer = 0

    def _init_fonts(self):
        def _f(size, bold=False):
            for fam in ('segoe ui', 'arial', 'helvetica', None):
                try:
                    return pygame.font.SysFont(fam, size, bold=bold)
                except Exception:
                    pass
            return pygame.font.Font(None, size)

        self.font_title   = _f(64, bold=True)
        self.font_sub     = _f(20)
        self.font_course  = _f(16)
        self.font_algo    = _f(18, bold=True)
        self.font_hint    = _f(14)
        self.font_cta     = _f(24, bold=True)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                return STATE_SELECT_MAP
            if event.key == pygame.K_e:
                return STATE_EDITOR
            if event.key in (pygame.K_q, pygame.K_ESCAPE):
                return STATE_QUIT
        if event.type == pygame.MOUSEBUTTONDOWN:
            return STATE_SELECT_MAP
        return None

    def update(self, dt):
        self.tick += 1
        for p in self._particles:
            p.update(self._rng)
        self._algo_timer += 1
        if self._algo_timer >= 120:
            self._algo_timer = 0
            self._algo_idx = (self._algo_idx + 1) % len(self._algo_names)

    def draw(self):
        surf = self.surface
        surf.fill(COLORS['bg'])

        self._draw_particles(surf)
        self._draw_title(surf)
        self._draw_algo_ticker(surf)
        self._draw_cta(surf)
        self._draw_hints(surf)

    def _draw_particles(self, surf):
        ps = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        for p in self._particles:
            r = max(1, int(p.radius))
            pygame.draw.circle(ps, (*p.color, p.alpha), (int(p.x), int(p.y)), r)
        surf.blit(ps, (0, 0))

    def _draw_title(self, surf):
        cx = WINDOW_W // 2
        cy = WINDOW_H // 2 - 80

        # Clean white title
        title_surf = self.font_title.render('AI Treasure Hunt', True, COLORS['text_primary'])
        title_rect = title_surf.get_rect(center=(cx, cy))
        surf.blit(title_surf, title_rect)

        # Colored underline bar (one segment per agent)
        bar_y = title_rect.bottom + 10
        bar_w = title_rect.width
        bar_x = cx - bar_w // 2
        seg_w = bar_w // len(AGENT_CONFIGS)
        for i, cfg in enumerate(AGENT_CONFIGS):
            pygame.draw.rect(surf, cfg['color'],
                             pygame.Rect(bar_x + i * seg_w, bar_y, seg_w, 3))

        # Subtitle
        sub_y = bar_y + 20
        sub_surf = self.font_sub.render(
            'Comparative Analysis of Search Algorithms', True, COLORS['text_secondary'])
        surf.blit(sub_surf, sub_surf.get_rect(center=(cx, sub_y)))

        # Course
        course_y = sub_y + 32
        course_surf = self.font_course.render(
            '21CSC206T -- Artificial Intelligence', True, COLORS['text_dim'])
        surf.blit(course_surf, course_surf.get_rect(center=(cx, course_y)))

    def _draw_algo_ticker(self, surf):
        cx = WINDOW_W // 2
        y  = WINDOW_H // 2 + 40

        text  = self._algo_names[self._algo_idx]
        color = AGENT_CONFIGS[self._algo_idx]['color']

        t    = self._algo_timer / 120.0
        fade = int(255 * min(1.0, min(t * 4, (1 - t) * 4)))

        algo_surf = self.font_algo.render(text, True, color)
        algo_surf.set_alpha(fade)
        algo_rect = algo_surf.get_rect(center=(cx, y))

        # Background pill
        pill = pygame.Surface((algo_rect.width + 24, algo_rect.height + 12), pygame.SRCALPHA)
        pill.fill((*COLORS['card_bg'], 180))
        surf.blit(pill, (algo_rect.x - 12, algo_rect.y - 6))
        pygame.draw.rect(surf, (*color, min(fade, 80)),
                         pygame.Rect(algo_rect.x - 12, algo_rect.y - 6,
                                     algo_rect.width + 24, algo_rect.height + 12),
                         border_radius=6, width=1)
        surf.blit(algo_surf, algo_rect)

    def _draw_cta(self, surf):
        cx = WINDOW_W // 2
        y  = WINDOW_H // 2 + 100
        blink = int((math.sin(self.tick * 0.06) + 1) / 2 * 100) + 155
        cta_surf = self.font_cta.render('Press Enter to Start', True,
                                        (blink, blink, 255))
        surf.blit(cta_surf, cta_surf.get_rect(center=(cx, y)))

    def _draw_hints(self, surf):
        hints = [
            ('[Enter / Space]  Play',  COLORS['text_secondary']),
            ('[E]  Map Editor',        COLORS['text_secondary']),
            ('[Q / Esc]  Quit',        COLORS['text_dim']),
        ]
        x = 30
        y = WINDOW_H - 30 - len(hints) * 22
        for text, color in hints:
            hs = self.font_hint.render(text, True, color)
            surf.blit(hs, (x, y))
            y += 22


_ALGO_DESC = {
    'bfs':    'Breadth-First Search -- optimal, level-by-level',
    'dfs':    'Depth-First Search -- deep dive, not optimal',
    'astar':  'A* Search -- f=g+h, optimal & efficient',
    'greedy': 'Greedy Best-First -- f=h, fast but risky',
}
