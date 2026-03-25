# AI Treasure Hunt

**21CSC206T — Artificial Intelligence | Unit 1, 2 & 3 Combined**

A multi-agent grid-world game where four AI agents race to find hidden treasure using different search algorithms. Watch BFS, DFS, A*, and Greedy Best-First Search compete side-by-side in real time with full step-by-step visualisation.

---

## Features

- **4 AI Agents** — BFS (Blue), DFS (Red), A\* (Teal), Greedy (Orange) racing simultaneously
- **4 Built-in Maps** — Simple Open, Maze Corridors, Dead End Traps, Random Maze
- **Interactive Map Editor** — draw custom walls, place start and treasure markers
- **Live Stats Panel** — nodes explored, path length, elapsed time, winner badge
- **Speed Control** — 6 simulation speeds (1×, 2×, 4×, 8×, 16×, 32×)
- **Pause / Resume** — freeze the race at any point
- **Agent Toggle** — enable/disable individual agents mid-race
- **Results Screen** — comparison table, bar charts, algorithm properties grid
- **Poster Generator** — generates a professional A3 poster using matplotlib

---

## Requirements

```
pygame>=2.1.0
matplotlib>=3.5.0
Pillow>=9.0.0
numpy>=1.21.0
```

### Installation

```bash
pip install -r requirements.txt
```

---

## How to Run

```bash
# From the project root (ai_treasure_hunt/)
python main.py
```

### Generate the Academic Poster

```bash
python poster/generate_poster.py
```

Output: `poster/AI_Treasure_Hunt_Poster.png`

---

## Controls

| Key | Action |
|-----|--------|
| `Enter` / `Space` | Start race / Pause-Resume |
| `R` | Restart with the same map |
| `N` | New random maze |
| `1` `2` `3` `4` | Toggle BFS / DFS / A\* / Greedy on-off |
| `+` / `-` | Increase / decrease simulation speed |
| `E` | Open Map Editor |
| `ESC` | Back to previous screen / Main menu |
| `Tab` | Skip to Results screen (when race is done) |

### Map Editor Controls

| Key / Action | Effect |
|---|---|
| `W` + left-drag | Place walls |
| `E` + left-drag | Erase walls |
| Right-click drag | Erase walls |
| `S` + click | Place Start marker |
| `T` + click | Place Treasure marker |
| `C` | Clear all interior walls |
| `Z` | Load Simple Open as template |
| `Enter` | Save and launch game |
| `Esc` | Discard and go back |

---

## Search Algorithms

### BFS — Breadth-First Search *(Blue)*
- **Strategy:** Queue (FIFO) — expands nodes level by level
- **Complete:** Yes | **Optimal:** Yes (fewest edges)
- **Complexity:** Time O(b^d), Space O(b^d)
- **Behaviour:** Explores outward evenly; guaranteed shortest path

### DFS — Depth-First Search *(Red)*
- **Strategy:** Stack (LIFO) — dives deep before backtracking
- **Complete:** Yes (on finite graphs) | **Optimal:** No
- **Complexity:** Time O(b^m), Space O(bm)
- **Behaviour:** Gets "lost" in long corridors; first path found may be very long

### A\* — A-Star Search *(Teal)*
- **Strategy:** Priority queue on f(n) = g(n) + h(n)
- **Complete:** Yes | **Optimal:** Yes (with admissible heuristic)
- **Heuristic:** Manhattan distance h(n) = |r₁−r₂| + |c₁−c₂|
- **Behaviour:** Guided toward goal; explores far fewer nodes than BFS

### Greedy Best-First *(Orange)*
- **Strategy:** Priority queue on f(n) = h(n) only
- **Complete:** No (can loop without visited tracking) | **Optimal:** No
- **Behaviour:** Rushes toward goal heuristically; fastest on open maps, easily fooled by obstacles

---

## File Structure

```
ai_treasure_hunt/
├── main.py                        # Entry point — ScreenManager loop
├── requirements.txt
├── README.md
│
├── game/
│   ├── __init__.py
│   ├── constants.py               # Window size, colours, agent configs, states
│   ├── algorithms.py              # BFS, DFS, A*, Greedy as generator functions
│   ├── agent.py                   # Agent class — wraps algorithm, tracks state
│   ├── grid.py                    # Grid class — wall/neighbour logic
│   ├── maps.py                    # 4 pre-built maps + random maze generator
│   ├── visualizer.py              # Pygame grid renderer (neon/cyberpunk theme)
│   └── stats_panel.py             # Right-side HUD — agent cards, speed, controls
│
├── screens/
│   ├── __init__.py
│   ├── title_screen.py            # Animated title with particle effects
│   ├── select_map_screen.py       # Map selection with preview thumbnails
│   ├── game_screen.py             # Main race screen
│   ├── results_screen.py          # Post-race comparison and charts
│   └── editor_screen.py           # Interactive map editor
│
├── poster/
│   └── generate_poster.py         # Standalone A3 poster generator (matplotlib)
│
└── assets/                        # (reserved for future sprites/sounds)
```

---

## Grading Criteria Covered

| CO | Topic | Where |
|----|-------|--------|
| CO1 | Problem Formulation (state space, initial/goal state, actions) | `algorithms.py`, `grid.py`, Results screen, Poster Section 1 |
| CO2 | Search Algorithms (BFS, DFS, A\*, Greedy) with properties | `algorithms.py`, `agent.py`, Results screen algorithm table |
| CO3 | Comparative Analysis (nodes, path length, time, completeness, optimality) | `results_screen.py`, `stats_panel.py`, Poster Section 4 |
| CO4 | Visualisation / Implementation | Full pygame application, step-by-step rendering in `visualizer.py` |

---

## Algorithm Comparison Summary

| Algorithm | Complete | Optimal | Time | Space |
|-----------|----------|---------|------|-------|
| BFS | Yes | Yes | O(b^d) | O(b^d) |
| DFS | No | No | O(b^m) | O(bm) |
| A\* | Yes | Yes | O(b^d) | O(b^d) |
| Greedy | No | No | O(b^m) | O(b^m) |

*b = branching factor, d = solution depth, m = maximum depth*

---

## Reference

Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson. Chapters 3–4.
#
