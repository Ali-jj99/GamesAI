# Game AI — Top-Down Combat Arena with Procedural Terrain

I built this as a university coursework project exploring game AI techniques in Python. The brief was to implement pathfinding, finite state machines, procedural generation, and probabilistic combat — and tie them all together into a working game. It ended up being one of those projects where every piece connects to every other piece, which made it genuinely fun to build (and occasionally painful to debug).

The game is a top-down arena where you fight AI-controlled enemies that think for themselves — they patrol, chase you, attack, retreat when hurt, and heal up before coming back. Two different enemy types use two different pathfinding algorithms, and the terrain actually affects how everyone moves.

![gameplay screenshot](report_assests/screenshots/gameplay.png)

## What I Built

The project is split into three sections that build on each other.

**Section 1** is the foundation. I designed a fixed 60x60 tile arena with four rooms, corridors, doorways, and a central crossroads. There are five terrain types — empty ground, walls, obstacles, mud, and rain — and the last two slow you down when you walk over them. I spawned four enemies into this arena: two EnemyTypeA that use A* pathfinding and two EnemyTypeB that use a cost-aware BFS. Both algorithms respect terrain weights, so enemies prefer faster routes even if they're longer. Each enemy runs a five-state FSM — patrol, chase, attack, retreat, and heal — with transitions driven by distance checks, line-of-sight raycasting, health thresholds, and a bravery factor that adds some randomness to their decisions. Combat uses probability-based damage rather than fixed values, so the two enemy types feel genuinely different to fight: TypeA is accurate and aggressive, TypeB hits harder but misses more.

**Section 2** is where I moved from hand-designed levels to procedural generation. I wrote a fractal noise system from scratch — a hash-based noise function, bilinear interpolation for smoothing, and multi-octave layering to get natural-looking results. Two separate noise passes generate a height map and a moisture map, which I combine to produce six terrain types: deep water, shallow water, ground, rock, forest, and hills. On top of that terrain I place six kinds of collectible artefacts (health potions, coins, weapons, shields, traps, loot chests), each with preferred terrain types for placement. Every artefact is validated as reachable from the player spawn using A* before it gets placed — no unreachable items. There's a path visualisation toggle so you can see the A* routes drawn on screen.

**Section 3** brings it all together. I wrote a terrain-to-arena mapping layer that converts the procedural terrain into the arena format Section 1 expects (forest becomes mud, hills become rain, water and rock become walls). That meant I could drop the entire combat system — FSM enemies, pathfinding, projectiles, probabilistic damage — onto a procedurally generated world without rewriting anything. Enemies spawn on validated walkable tiles, artefacts are scattered across the landscape, and the full AI runs exactly as it does in the fixed arena.

## Tech Stack

- **Python 3.10+**
- **Pygame** — rendering, input, game loop
- **NumPy** — grid operations and terrain generation

## Getting Started

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run

There are three entry points, one per section:

```bash
# Section 1 — Fixed arena with FSM enemies and combat
python main.py

# Section 2 — Procedural terrain with artefacts
python main_section2.py

# Section 3 — Combined model (procedural terrain + combat)
python main_combined.py
```

## Controls

| Key | Action |
|-----|--------|
| WASD / Arrow keys | Move |
| Left mouse click | Shoot |
| P | Toggle path visualisation (Section 2) |
| Tab / F1 | Toggle debug mode (Sections 1 & 3) |
| Escape | Quit (Sections 2 & 3) |

## Project Structure

```
.
├── main.py                        # Section 1 entry — fixed arena + combat
├── main_section2.py               # Section 2 entry — procedural terrain
├── main_combined.py               # Section 3 entry — combined model
├── ai/
│   └── pathfinding.py             # A* and cost-aware BFS algorithms
├── core/
│   └── damage_models.py           # Probability-based damage calculations
├── entities/
│   ├── player.py                  # Player movement with terrain speed modifiers
│   ├── enemy_base.py              # Base enemy class with 5-state FSM
│   ├── enemy_type_a.py            # Aggressive enemy using A* pathfinding
│   ├── enemy_type_b.py            # Cautious enemy using BFS pathfinding
│   ├── projectile.py              # Projectile physics and wall collision
│   └── artefacts.py               # Six collectible artefact types
├── world/
│   ├── arena_generator.py         # Hand-designed arena layout for Section 1
│   ├── procedural_terrain.py      # Fractal noise terrain generation
│   └── artefact_spawner.py        # Terrain-aware artefact placement with A* validation
├── scenes/
│   └── terrain_scene.py           # Section 2 game loop and rendering
├── report_assests/
│   ├── data/                      # Performance timing data
│   └── screenshots/               # Gameplay screenshots
├── tests/
├── ui/
├── requirements.txt
├── LICENSE
└── .gitignore
```

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
