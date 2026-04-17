"""Constants and configuration for AI Treasure Hunt."""
import os

# --- Window ---
WINDOW_W     = 1400
WINDOW_H     = 800
PANEL_W      = 320
BOTTOM_BAR_H = 50
GRID_W       = WINDOW_W - PANEL_W       # 1080
GRID_H       = WINDOW_H - BOTTOM_BAR_H  # 750

# --- Grid ---
GRID_COLS = 30
GRID_ROWS = 20
CELL_W    = GRID_W // GRID_COLS   # 36
CELL_H    = GRID_H // GRID_ROWS   # 37
CELL_GAP  = 1                     # gap between cells (acts as visual separator)

# --- Timing ---
FPS               = 60
SPEEDS            = [1, 2, 4, 8, 16, 32]
DEFAULT_SPEED_IDX = 0

# --- Colors (R,G,B) — matches spec exactly ---
COLORS = {
    # Background & grid
    'bg'            : ( 30,  30,  46),   # #1E1E2E deep charcoal
    'wall'          : ( 58,  58,  74),   # #3A3A4A medium gray walls
    'open'          : ( 42,  42,  58),   # #2A2A3A slightly lighter than bg
    'panel_bg'      : ( 37,  37,  53),   # #252535
    # Agent colors
    'bfs'           : ( 74, 169, 255),   # #4A9EFF clean blue
    'dfs'           : (255, 184,  48),   # #FFB830 amber/yellow
    'astar'         : ( 80, 227, 164),   # #50E3A4 mint green
    'greedy'        : (255, 107, 107),   # #FF6B6B coral red
    # Markers
    'start'         : ( 80, 227, 164),   # #50E3A4 green square
    'treasure'      : (255,  71,  87),   # #FF4757 red
    # Text
    'text_primary'  : (255, 255, 255),   # #FFFFFF
    'text_secondary': (136, 136, 170),   # #8888AA muted gray
    'text_dim'      : ( 90,  90, 120),
    # UI
    'panel_border'  : ( 50,  50,  70),
    'card_bg'       : ( 37,  37,  53),   # #252535
    'success'       : ( 80, 227, 164),
    'failure'       : (255, 107, 107),
    'highlight'     : (180, 180, 255),
    'white'         : (255, 255, 255),
    'black'         : (  0,   0,   0),
}

# Explored cell alpha (35% opacity)
EXPLORED_ALPHA = 89  # 255 * 0.35 ~ 89

# --- Agent configs ---
AGENT_CONFIGS = [
    {'name': 'BFS',    'algo_key': 'bfs',    'color': COLORS['bfs']},
    {'name': 'DFS',    'algo_key': 'dfs',    'color': COLORS['dfs']},
    {'name': 'A*',     'algo_key': 'astar',  'color': COLORS['astar']},
    {'name': 'Greedy', 'algo_key': 'greedy', 'color': COLORS['greedy']},
]

# --- Screen states ---
STATE_TITLE      = 'title'
STATE_SELECT_MAP = 'select_map'
STATE_GAME       = 'game'
STATE_RESULTS    = 'results'
STATE_EDITOR     = 'editor'
STATE_QUIT       = 'quit'

# --- Map names ---
MAP_NAMES = ['Simple Open', 'Maze Corridors', 'Dead End Traps', 'Random Maze']

# --- Assets path ---
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
