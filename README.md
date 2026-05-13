# Game AI: Top Down Combat Arena with Procedural Terrain

I built this for a university coursework on game AI. The assignment was to implement pathfinding, finite state machines, procedural generation, and probabilistic combat, then tie them all together into a working game. It turned into one of those projects where every piece connects to every other piece, which made it genuinely fun to build and occasionally painful to debug.

You play in a top down arena fighting enemies that think for themselves. They patrol around, chase you down, attack, retreat when they're hurt, and heal up before coming back for more. Two different enemy types use two different pathfinding algorithms, and the terrain actually affects how everyone moves.

![gameplay screenshot](report_assests/screenshots/gameplay.png)

## What I Built

I split the project into three sections that build on each other.

Section 1 is the foundation. I designed a fixed 60x60 tile arena with four rooms, corridors, doorways, and a central crossroads. There are five terrain types: empty ground, walls, obstacles, mud, and rain. The last two slow you down when you walk over them. I spawned four enemies into this arena. Two of them are EnemyTypeA and use A* pathfinding, and the other two are EnemyTypeB and use a cost aware BFS. Both algorithms respect terrain weights, so enemies will prefer a faster route even if it's longer. Each enemy runs a five state FSM with patrol, chase, attack, retreat, and heal. State transitions are driven by distance checks, line of sight raycasting, health thresholds, and a bravery factor that adds randomness to their decisions. I also implemented probability based damage instead of fixed values, which makes the two enemy types feel genuinely different to fight. TypeA is accurate and aggressive. TypeB hits harder but misses more often.

Section 2 is where I moved from hand designed levels to procedural generation. I wrote a fractal noise system from scratch. It starts with a hash based noise function, then I apply bilinear interpolation to smooth things out, and finally I layer multiple octaves together to get natural looking terrain. Two separate noise passes generate a height map and a moisture map, and I combine them to produce six terrain types: deep water, shallow water, ground, rock, forest, and hills. On top of that I place six kinds of collectible artefacts (health potions, coins, weapons, shields, traps, and loot chests), each with preferred terrain types for placement. Every single artefact gets validated as reachable from the player spawn using A* before it actually gets placed, so there are never any unreachable items. I also added a path visualisation toggle so you can see the A* routes drawn on screen in real time.

Section 3 brings everything together. I wrote a mapping layer that converts the procedural terrain into the arena tile format that Section 1 expects. Forest becomes mud, hills become rain, water and rock become walls. That meant I could drop the entire combat system onto a procedurally generated world without rewriting anything. The FSM enemies, pathfinding, projectiles, and probabilistic damage all just work. Enemies spawn on validated walkable tiles, artefacts are scattered across the landscape, and the full AI runs exactly as it does in the fixed arena.

## Tech Stack

I used Python 3.10+ with Pygame for rendering, input handling, and the game loop. NumPy handles all the grid operations and terrain generation.

## Getting Started

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run

There are three entry points, one per section:

```bash
# Section 1: Fixed arena with FSM enemies and combat
python main.py

# Section 2: Procedural terrain with artefacts
python main_section2.py

# Section 3: Combined model with procedural terrain and combat
python main_combined.py
```

## Controls

| Key | Action |
|-----|--------|
| WASD / Arrow keys | Move |
| Left mouse click | Shoot |
| P | Toggle path visualisation (Section 2) |
| Tab / F1 | Toggle debug mode (Sections 1 and 3) |
| Escape | Quit (Sections 2 and 3) |

## Project Structure

```
.
├── main.py                        # Section 1 entry point, fixed arena and combat
├── main_section2.py               # Section 2 entry point, procedural terrain
├── main_combined.py               # Section 3 entry point, combined model
├── ai/
│   └── pathfinding.py             # A* and cost aware BFS algorithms
├── core/
│   └── damage_models.py           # Probability based damage calculations
├── entities/
│   ├── player.py                  # Player movement with terrain speed modifiers
│   ├── enemy_base.py              # Base enemy class with five state FSM
│   ├── enemy_type_a.py            # Aggressive enemy, uses A* pathfinding
│   ├── enemy_type_b.py            # Cautious enemy, uses BFS pathfinding
│   ├── projectile.py              # Projectile physics and wall collision
│   └── artefacts.py               # Six collectible artefact types
├── world/
│   ├── arena_generator.py         # Hand designed arena layout for Section 1
│   ├── procedural_terrain.py      # Fractal noise terrain generation
│   └── artefact_spawner.py        # Terrain aware artefact placement with A* validation
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

MIT License. See the [LICENSE](LICENSE) file for details.
