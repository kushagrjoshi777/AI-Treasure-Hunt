"""
AI Treasure Hunt — Poster Generator
21CSC206T Artificial Intelligence

Generates a professional A3-landscape poster using matplotlib + PIL only.
Run with:  python poster/generate_poster.py

Output: poster/AI_Treasure_Hunt_Poster.png
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D

# ── Output path ───────────────────────────────────────────────────────────────
_SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PNG   = os.path.join(_SCRIPT_DIR, 'AI_Treasure_Hunt_Poster.png')
OUTPUT_PDF   = os.path.join(_SCRIPT_DIR, 'AI_Treasure_Hunt_Poster.pdf')
os.makedirs(_SCRIPT_DIR, exist_ok=True)

# ── Colour palette (matches game spec exactly) ────────────────────────────────
BG_DARK   = '#1E1E2E'
BG_PANEL  = '#252535'
BG_CARD   = '#2A2A3A'
COL_BFS   = '#4A9EFF'
COL_DFS   = '#FFB830'
COL_ASTAR = '#50E3A4'
COL_GRD   = '#FF6B6B'
COL_WHITE = '#ffffff'
COL_GOLD  = '#FFB830'
COL_SEC   = '#8888AA'
COL_DIM   = '#5A5A78'

ALGO_COLORS = [COL_BFS, COL_DFS, COL_ASTAR, COL_GRD]
ALGO_NAMES  = ['BFS', 'DFS', 'A*', 'Greedy']

# ── Figure setup ─────────────────────────────────────────────────────────────
# A3 landscape at 150 DPI → 5906×4134 px ÷ 2 = 2953×2067 for ~300DPI equivalent
DPI    = 150
FIG_W  = 5906 / DPI   # ≈ 39.4 in
FIG_H  = 4134 / DPI   # ≈ 27.6 in

fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor=BG_DARK, dpi=DPI)

# ── Grid layout ──────────────────────────────────────────────────────────────
# Row 0: title (small)
# Row 1: content (3 columns)
# Row 2: bottom strip (small)
outer = gridspec.GridSpec(
    3, 1,
    figure=fig,
    height_ratios=[0.12, 0.78, 0.10],
    hspace=0.03,
    left=0.02, right=0.98, top=0.98, bottom=0.02,
)

# Content columns: left | middle | right
content = gridspec.GridSpecFromSubplotSpec(
    1, 3,
    subplot_spec=outer[1],
    wspace=0.04,
    width_ratios=[1, 1, 1],
)

# Left column: 2 sub-rows
left_col = gridspec.GridSpecFromSubplotSpec(
    2, 1,
    subplot_spec=content[0],
    hspace=0.06,
    height_ratios=[1, 1],
)

# Middle column: 2 sub-rows
mid_col = gridspec.GridSpecFromSubplotSpec(
    2, 1,
    subplot_spec=content[1],
    hspace=0.06,
    height_ratios=[1.1, 0.9],
)

# Right column: 2 sub-rows
right_col = gridspec.GridSpecFromSubplotSpec(
    2, 1,
    subplot_spec=content[2],
    hspace=0.06,
    height_ratios=[1, 1],
)


# ─────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────────────────────────────────────

def dark_ax(ax, border_color='#323248', title_text=None, title_color=COL_GOLD):
    """Style an axes with the dark theme."""
    ax.set_facecolor(BG_PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(border_color)
        spine.set_linewidth(1.5)
    ax.tick_params(colors=COL_SEC, labelsize=8)
    if title_text:
        ax.set_title(title_text, color=title_color, fontsize=11,
                     fontweight='bold', pad=6, loc='left')
    return ax


def section_box(ax, label, color=COL_GOLD):
    """Draw a coloured top-border section label above the axes content."""
    ax.axhline(y=1.0, xmin=0, xmax=1, color=color, linewidth=3,
               clip_on=False)
    ax.text(0.01, 1.02, label, transform=ax.transAxes,
            color=color, fontsize=10, fontweight='bold', va='bottom')


def text_block(ax, lines, x=0.04, y=0.95, spacing=0.09,
               colors=None, sizes=None, bold_mask=None):
    """Render a list of text lines inside an axes."""
    if colors    is None: colors    = [COL_WHITE] * len(lines)
    if sizes     is None: sizes     = [9]         * len(lines)
    if bold_mask is None: bold_mask = [False]      * len(lines)
    for i, (line, c, s, b) in enumerate(zip(lines, colors, sizes, bold_mask)):
        ax.text(x, y - i * spacing, line,
                transform=ax.transAxes,
                color=c, fontsize=s,
                fontweight='bold' if b else 'normal',
                va='top')


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 0 — TITLE BAR
# ─────────────────────────────────────────────────────────────────────────────

ax_title = fig.add_subplot(outer[0])
ax_title.set_facecolor(BG_DARK)
ax_title.axis('off')

# Gradient-style coloured band
for i, color in enumerate(ALGO_COLORS):
    ax_title.add_patch(Rectangle(
        (i / 4, 0), 1 / 4, 0.18,
        transform=ax_title.transAxes,
        color=color, alpha=0.25, zorder=0
    ))

ax_title.text(0.5, 0.78, 'AI TREASURE HUNT',
              transform=ax_title.transAxes,
              ha='center', va='top',
              color=COL_WHITE, fontsize=52, fontweight='bold')

ax_title.text(0.5, 0.40,
              'Comparative Analysis of Search Algorithms in a Multi-Agent Grid World',
              transform=ax_title.transAxes,
              ha='center', va='top',
              color=COL_SEC, fontsize=17)

ax_title.text(0.5, 0.12,
              '21CSC206T — Artificial Intelligence  |  Unit 1, 2 & 3 Combined  |  '
              '[YOUR NAME]  |  [REG NO]  |  [SECTION]',
              transform=ax_title.transAxes,
              ha='center', va='top',
              color=COL_DIM, fontsize=11)

# Coloured underline bar
for i, color in enumerate(ALGO_COLORS):
    ax_title.add_patch(Rectangle(
        (i / 4, 0), 1 / 4, 0.04,
        transform=ax_title.transAxes,
        color=color, zorder=2
    ))


# ─────────────────────────────────────────────────────────────────────────────
# LEFT COLUMN — top: PROBLEM FORMULATION  |  bottom: STATE SPACE DIAGRAM
# ─────────────────────────────────────────────────────────────────────────────

# ── Left-Top: Problem Formulation ────────────────────────────────────────────
ax_pf = fig.add_subplot(left_col[0])
dark_ax(ax_pf, border_color='#323248')
ax_pf.axis('off')
section_box(ax_pf, 'PROBLEM FORMULATION  (CO1)', color=COL_ASTAR)

formulation = [
    ('STATE SPACE',   'Grid positions (r, c)  where  0 ≤ r < 20,  0 ≤ c < 30'),
    ('INITIAL STATE', 'Agent at start cell  (18, 1)  — bottom-left region'),
    ('GOAL STATE',    'Agent reaches treasure cell  (1, 28)  — top-right'),
    ('ACTIONS',       'Move { North, South, East, West } to adjacent non-wall cells'),
    ('PATH COST',     'Each step costs 1  (uniform-cost edges)'),
    ('HEURISTIC h',   'Manhattan distance: h(n) = |r₁−r₂| + |c₁−c₂|'),
]

y = 0.88
for label, desc in formulation:
    ax_pf.text(0.02, y, f'{label}:', color=COL_GOLD,
               transform=ax_pf.transAxes, fontsize=8.5, fontweight='bold', va='top')
    ax_pf.text(0.28, y, desc, color=COL_WHITE,
               transform=ax_pf.transAxes, fontsize=8.5, va='top')
    y -= 0.12

# Formula box for f(n)
formula_box = FancyBboxPatch((0.01, 0.04), 0.97, 0.10,
                              boxstyle='round,pad=0.01',
                              linewidth=1.5,
                              edgecolor=COL_ASTAR,
                              facecolor='#1E1E2E',
                              transform=ax_pf.transAxes)
ax_pf.add_patch(formula_box)
ax_pf.text(0.5, 0.09, 'A* Evaluation:  f(n) = g(n) + h(n)    '
           'where  g(n) = cost from start,  h(n) = Manhattan distance to goal',
           transform=ax_pf.transAxes,
           ha='center', va='center',
           color=COL_ASTAR, fontsize=9, fontweight='bold')


# ── Left-Bottom: State Space Diagram ─────────────────────────────────────────
ax_diag = fig.add_subplot(left_col[1])
dark_ax(ax_diag, border_color='#323248')
ax_diag.set_xlim(0, 10)
ax_diag.set_ylim(0, 8)
ax_diag.axis('off')
section_box(ax_diag, 'STATE SPACE DIAGRAM', color=COL_ASTAR)

# Draw a 5×5 mini grid
GRID_COLS_D = 5
GRID_ROWS_D = 5
CELL = 1.2
OX, OY = 0.4, 0.8

WALLS_D  = {(0, 1), (0, 4), (1, 3), (2, 0), (3, 2), (4, 1)}
START_D  = (4, 0)
GOAL_D   = (0, 4)

for r in range(GRID_ROWS_D):
    for c in range(GRID_COLS_D):
        x = OX + c * CELL
        y = OY + (GRID_ROWS_D - 1 - r) * CELL
        if (r, c) in WALLS_D:
            fc = '#3A3A4A'
            ec = '#4A4A5A'
            lbl = 'X'
            tc  = COL_DIM
        elif (r, c) == START_D:
            fc = '#1a3a2a'
            ec = '#50E3A4'
            lbl = 'S'
            tc  = '#50E3A4'
        elif (r, c) == GOAL_D:
            fc = '#3a1a1a'
            ec = '#FF4757'
            lbl = 'G'
            tc  = '#FF4757'
        else:
            fc = BG_PANEL
            ec = '#323248'
            lbl = ''
            tc  = COL_SEC
        ax_diag.add_patch(Rectangle((x, y), CELL * 0.92, CELL * 0.92,
                                    facecolor=fc, edgecolor=ec, linewidth=1.2))
        if lbl:
            ax_diag.text(x + CELL * 0.46, y + CELL * 0.46, lbl,
                         ha='center', va='center',
                         color=tc, fontsize=11, fontweight='bold')

# Draw action arrows from cell (2,2)
ac_r, ac_c = 2, 2
ax2 = OX + ac_c * CELL + CELL * 0.46
ay2 = OY + (GRID_ROWS_D - 1 - ac_r) * CELL + CELL * 0.46

arrow_kw = dict(arrowstyle='->', color=COL_GOLD,
                lw=1.5, mutation_scale=14,
                transform=ax_diag.transData)

DIRECTIONS = [
    (0,  CELL * 0.8, 'N'),
    (0, -CELL * 0.8, 'S'),
    (-CELL * 0.8, 0, 'W'),
    ( CELL * 0.8, 0, 'E'),
]
for dx, dy, label in DIRECTIONS:
    ax_diag.annotate('', xy=(ax2 + dx, ay2 + dy), xytext=(ax2, ay2),
                     arrowprops=dict(arrowstyle='->', color=COL_GOLD, lw=1.5))
    ax_diag.text(ax2 + dx * 1.25, ay2 + dy * 1.25, label,
                 color=COL_GOLD, fontsize=8, ha='center', va='center')

# Legend
legend_y = 0.10
legend_items = [
    (Rectangle((0, 0), 1, 1, fc='#1a3a2a', ec='#50E3A4'), 'Start (S)'),
    (Rectangle((0, 0), 1, 1, fc='#3a1a1a', ec='#FF4757'),  'Goal (G)'),
    (Rectangle((0, 0), 1, 1, fc='#3A3A4A', ec='#4A4A5A'), 'Wall (X)'),
    (Rectangle((0, 0), 1, 1, fc=BG_PANEL,  ec='#323248'), 'Open cell'),
]
ax_diag.legend(handles=[p for p, _ in legend_items],
               labels=[l for _, l in legend_items],
               loc='lower left',
               facecolor=BG_PANEL, edgecolor='#323248',
               labelcolor=COL_SEC, fontsize=8,
               bbox_to_anchor=(0.0, 0.0))

ax_diag.text(8.0, 0.4,
             'Each non-wall cell is a\nstate. Edges connect\nadjacent open cells.',
             color=COL_SEC, fontsize=8, va='bottom')


# ─────────────────────────────────────────────────────────────────────────────
# MIDDLE COLUMN — top: SEARCH ALGORITHMS TABLE  |  bottom: DESCRIPTIONS
# ─────────────────────────────────────────────────────────────────────────────

# ── Middle-Top: Algorithm Table ───────────────────────────────────────────────
ax_table = fig.add_subplot(mid_col[0])
dark_ax(ax_table, border_color='#323248')
ax_table.axis('off')
section_box(ax_table, 'SEARCH ALGORITHMS  (CO2)', color=COL_BFS)

COL_LABELS  = ['Algorithm', 'Complete', 'Optimal', 'Time', 'Space']
TABLE_DATA  = [
    ['BFS',    'Yes', 'Yes', 'O(b^d)', 'O(b^d)'],
    ['DFS',    'No',  'No',  'O(b^m)', 'O(bm)'],
    ['A*',     'Yes', 'Yes', 'O(b^d)', 'O(b^d)'],
    ['Greedy', 'No',  'No',  'O(b^m)', 'O(b^m)'],
]
ROW_COLORS = [COL_BFS, COL_DFS, COL_ASTAR, COL_GRD]

COL_XS     = [0.01, 0.22, 0.39, 0.56, 0.78]
HEADER_Y   = 0.88
ROW_H      = 0.13
HEADER_BG  = FancyBboxPatch((0.0, HEADER_Y - 0.02), 1.0, 0.07,
                              boxstyle='square,pad=0',
                              linewidth=0, facecolor='#1E1E2E',
                              transform=ax_table.transAxes)
ax_table.add_patch(HEADER_BG)

for xi, col_label in zip(COL_XS, COL_LABELS):
    ax_table.text(xi, HEADER_Y, col_label,
                  transform=ax_table.transAxes,
                  color=COL_SEC, fontsize=8.5, fontweight='bold', va='top')

for ri, (row, row_color) in enumerate(zip(TABLE_DATA, ROW_COLORS)):
    ry = HEADER_Y - 0.06 - (ri + 1) * ROW_H
    # Row background
    bg = FancyBboxPatch((0.0, ry - 0.01), 1.0, ROW_H - 0.01,
                         boxstyle='square,pad=0',
                         linewidth=0,
                         facecolor=row_color + '18',
                         transform=ax_table.transAxes)
    ax_table.add_patch(bg)
    # Left accent bar
    ax_table.add_patch(Rectangle((0.0, ry - 0.01), 0.012, ROW_H - 0.01,
                                  facecolor=row_color, transform=ax_table.transAxes))
    for xi, cell in zip(COL_XS, row):
        is_yes = (cell == 'Yes')
        is_no  = (cell == 'No')
        cc = COL_ASTAR if is_yes else (COL_DFS if is_no else COL_WHITE)
        if xi == COL_XS[0]:
            cc = row_color
        ax_table.text(xi + 0.01, ry + ROW_H * 0.38, cell,
                      transform=ax_table.transAxes,
                      color=cc, fontsize=9,
                      fontweight='bold' if xi == COL_XS[0] else 'normal',
                      va='center')

# Grid lines
for yi_frac in [HEADER_Y - 0.02] + [HEADER_Y - 0.06 - (i + 1) * ROW_H
                                      for i in range(4)]:
    ax_table.plot([0, 1], [yi_frac, yi_frac], color='#323248', linewidth=0.8,
                  transform=ax_table.transAxes, clip_on=False)


# ── Middle-Bottom: Algorithm Descriptions ────────────────────────────────────
ax_algos = fig.add_subplot(mid_col[1])
dark_ax(ax_algos, border_color='#323248')
ax_algos.axis('off')
section_box(ax_algos, 'ALGORITHM DESCRIPTIONS', color=COL_BFS)

descs = [
    (COL_BFS,   'BFS  — Breadth-First Search',
                'Queue (FIFO) · explores level by level · guarantees shortest path'),
    (COL_DFS,   'DFS  — Depth-First Search',
                'Stack (LIFO) · dives deep before backtracking · not optimal'),
    (COL_ASTAR, 'A*   — A-Star Search',
                'Priority queue · f(n) = g(n) + h(n) · optimal with admissible h'),
    (COL_GRD,   'Greedy — Greedy Best-First',
                'Priority queue · f(n) = h(n) only · fast but may miss optimal path'),
]

y = 0.91
for color, title, detail in descs:
    # Coloured label box
    box = FancyBboxPatch((0.01, y - 0.10), 0.97, 0.11,
                          boxstyle='round,pad=0.01',
                          linewidth=1.2, edgecolor=color,
                          facecolor=color + '18',
                          transform=ax_algos.transAxes)
    ax_algos.add_patch(box)
    ax_algos.text(0.04, y - 0.01, title,
                  transform=ax_algos.transAxes,
                  color=color, fontsize=9.5, fontweight='bold', va='top')
    ax_algos.text(0.04, y - 0.055, detail,
                  transform=ax_algos.transAxes,
                  color=COL_SEC, fontsize=8.5, va='top')
    y -= 0.19

# f(n) formula box
form_box = FancyBboxPatch((0.01, 0.04), 0.97, 0.14,
                           boxstyle='round,pad=0.01',
                           linewidth=1.5, edgecolor=COL_GOLD,
                           facecolor='#2A2A3A',
                           transform=ax_algos.transAxes)
ax_algos.add_patch(form_box)
ax_algos.text(0.5, 0.14,
              'Key formulae:   f(n) = g(n) + h(n)   [A*]     '
              'f(n) = h(n)   [Greedy]     h(n) = |r₁−r₂| + |c₁−c₂|   [Manhattan]',
              transform=ax_algos.transAxes,
              ha='center', va='center',
              color=COL_GOLD, fontsize=9, fontweight='bold')


# ─────────────────────────────────────────────────────────────────────────────
# RIGHT COLUMN — top: GAME ARCHITECTURE  |  bottom: SAMPLE RESULTS + CHARTS
# ─────────────────────────────────────────────────────────────────────────────

# ── Right-Top: Game Architecture Flowchart ────────────────────────────────────
ax_arch = fig.add_subplot(right_col[0])
dark_ax(ax_arch, border_color='#323248')
ax_arch.set_xlim(0, 10)
ax_arch.set_ylim(0, 10)
ax_arch.axis('off')
section_box(ax_arch, 'GAME ARCHITECTURE', color=COL_GRD)

FLOW_STEPS = [
    (5.0, 9.2, 'Start',             COL_GOLD),
    (5.0, 7.7, 'Title Screen',      COL_BFS),
    (5.0, 6.2, 'Select Map',        COL_BFS),
    (5.0, 4.7, 'Initialise Agents', COL_ASTAR),
    (5.0, 3.2, 'Run Search (×4)',   COL_ASTAR),
    (5.0, 1.7, 'Visualise Steps',   COL_GRD),
    (5.0, 0.3, 'Compare Results',   COL_GRD),
]
BOX_W, BOX_H = 3.8, 0.85

for bx, by, label, color in FLOW_STEPS:
    ax_arch.add_patch(FancyBboxPatch(
        (bx - BOX_W / 2, by - BOX_H / 2), BOX_W, BOX_H,
        boxstyle='round,pad=0.08',
        linewidth=1.5, edgecolor=color,
        facecolor=color + '22',
    ))
    ax_arch.text(bx, by, label, ha='center', va='center',
                 color=color, fontsize=9.5, fontweight='bold')

# Arrows between boxes
for i in range(len(FLOW_STEPS) - 1):
    _, y1, _, c1 = FLOW_STEPS[i]
    _, y2, _, c2 = FLOW_STEPS[i + 1]
    ax_arch.annotate('',
                     xy=(5.0, y2 + BOX_H / 2 + 0.05),
                     xytext=(5.0, y1 - BOX_H / 2 - 0.05),
                     arrowprops=dict(arrowstyle='->', color=COL_DIM, lw=1.5))

# Side note: four agents in parallel
ax_arch.text(9.0, 3.2,
             'BFS\nDFS\nA*\nGreedy',
             ha='center', va='center',
             color=COL_SEC, fontsize=8,
             bbox=dict(boxstyle='round', fc=BG_PANEL, ec='#323248'))
ax_arch.annotate('', xy=(6.9, 3.2), xytext=(8.0, 3.2),
                 arrowprops=dict(arrowstyle='<-', color=COL_DIM, lw=1.2))


# ── Right-Bottom: Sample Results + Bar Charts ─────────────────────────────────
# Split this area into two: table on left, charts on right
right_bottom = gridspec.GridSpecFromSubplotSpec(
    1, 2, subplot_spec=right_col[1], wspace=0.04, width_ratios=[1.1, 1.6]
)

ax_res_table = fig.add_subplot(right_bottom[0])
dark_ax(ax_res_table, border_color='#323248')
ax_res_table.axis('off')
section_box(ax_res_table, 'SAMPLE RESULTS  (CO3)', color=COL_GRD)

RESULT_DATA = [
    ('BFS',    312,  45, '0.82s'),
    ('DFS',    489,  67, '0.94s'),
    ('A*',     124,  45, '0.31s'),
    ('Greedy',  89,  52, '0.18s'),
]
RES_COL_XS = [0.01, 0.30, 0.58, 0.80]
RES_HEADERS = ['Agent', 'Nodes', 'Path', 'Time']

header_y = 0.88
for xi, hdr in zip(RES_COL_XS, RES_HEADERS):
    ax_res_table.text(xi, header_y, hdr,
                      transform=ax_res_table.transAxes,
                      color=COL_SEC, fontsize=8.5, fontweight='bold', va='top')

for ri, (name, nodes, path_len, t) in enumerate(RESULT_DATA):
    ry = header_y - 0.09 - ri * 0.16
    rc = ALGO_COLORS[ri]
    bg = FancyBboxPatch((0.0, ry - 0.02), 1.0, 0.14,
                         boxstyle='square,pad=0',
                         linewidth=0, facecolor=rc + '18',
                         transform=ax_res_table.transAxes)
    ax_res_table.add_patch(bg)
    ax_res_table.add_patch(Rectangle((0.0, ry - 0.02), 0.015, 0.14,
                                      facecolor=rc,
                                      transform=ax_res_table.transAxes))
    for xi, val in zip(RES_COL_XS,
                       [name, str(nodes), str(path_len), t]):
        cc = rc if xi == RES_COL_XS[0] else COL_WHITE
        ax_res_table.text(xi + 0.02, ry + 0.05, val,
                          transform=ax_res_table.transAxes,
                          color=cc, fontsize=9,
                          fontweight='bold' if xi == RES_COL_XS[0] else 'normal',
                          va='center')

note = '* Simulated data on Simple Open map'
ax_res_table.text(0.02, 0.05, note,
                  transform=ax_res_table.transAxes,
                  color=COL_DIM, fontsize=7.5, va='bottom')


# ── Bar Charts ────────────────────────────────────────────────────────────────
ax_charts = fig.add_subplot(right_bottom[1])
dark_ax(ax_charts, border_color='#323248')
ax_charts.axis('off')

# Split into two sub-axes stacked vertically
charts_spec = gridspec.GridSpecFromSubplotSpec(
    2, 1, subplot_spec=right_bottom[1], hspace=0.45,
)

ax_nodes = fig.add_subplot(charts_spec[0])
ax_paths = fig.add_subplot(charts_spec[1])

names  = [r[0] for r in RESULT_DATA]
nodes  = [r[1] for r in RESULT_DATA]
paths  = [r[2] for r in RESULT_DATA]
x      = np.arange(len(names))

for ax_bar, values, ylabel, title, color_set in [
    (ax_nodes, nodes, 'Nodes', 'Nodes Explored', ALGO_COLORS),
    (ax_paths, paths, 'Length', 'Path Length',   ALGO_COLORS),
]:
    dark_ax(ax_bar, border_color='#323248', title_text=title, title_color=COL_GRD)
    bars = ax_bar.bar(x, values, color=color_set, width=0.6,
                      edgecolor='#323248', linewidth=0.8)
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(names, color=COL_SEC, fontsize=8)
    ax_bar.set_ylabel(ylabel, color=COL_SEC, fontsize=8)
    ax_bar.tick_params(axis='y', colors=COL_SEC, labelsize=7)
    ax_bar.set_facecolor(BG_PANEL)
    ax_bar.yaxis.label.set_color(COL_SEC)

    for bar, val in zip(bars, values):
        ax_bar.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                    str(val), ha='center', va='bottom',
                    color=COL_WHITE, fontsize=8, fontweight='bold')


# ─────────────────────────────────────────────────────────────────────────────
# BOTTOM STRIP — AI Concepts + References
# ─────────────────────────────────────────────────────────────────────────────

ax_bottom = fig.add_subplot(outer[2])
ax_bottom.set_facecolor(BG_PANEL)
for spine in ax_bottom.spines.values():
    spine.set_edgecolor('#323248')
ax_bottom.axis('off')

concepts_title = 'AI CONCEPTS DEMONSTRATED:'
concepts = ('State Space Search  |  Heuristic Functions  |  Admissibility & Consistency  |  '
            'Completeness vs Optimality  |  Informed vs Uninformed Search  |  '
            'Algorithm Complexity Analysis')

ref = 'Reference: Russell & Norvig, Artificial Intelligence: A Modern Approach, 4th Ed. — Chapters 3, 4'

ax_bottom.text(0.01, 0.75, concepts_title,
               transform=ax_bottom.transAxes,
               color=COL_GOLD, fontsize=10, fontweight='bold', va='top')
ax_bottom.text(0.22, 0.75, concepts,
               transform=ax_bottom.transAxes,
               color=COL_WHITE, fontsize=9.5, va='top')
ax_bottom.text(0.5, 0.18, ref,
               transform=ax_bottom.transAxes,
               ha='center', va='top',
               color=COL_DIM, fontsize=9)


# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────

fig.savefig(OUTPUT_PNG, dpi=DPI, bbox_inches='tight',
            facecolor=BG_DARK, edgecolor='none')
fig.savefig(OUTPUT_PDF, dpi=DPI, bbox_inches='tight',
            facecolor=BG_DARK, edgecolor='none')
plt.close(fig)

print(f'Poster saved to:')
print(f'  PNG: {OUTPUT_PNG}')
print(f'  PDF: {OUTPUT_PDF}')
