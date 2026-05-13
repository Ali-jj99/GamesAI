# This file generates artefacts with terrain-based placement and accessibility validation for Section 2.2

import random
import numpy as np
from typing import List, Tuple, Optional
from entities.artefacts import Artefact, ARTEFACT_HEALTH_POTION, ARTEFACT_COIN, ARTEFACT_WEAPON, \
    ARTEFACT_SHIELD, ARTEFACT_TRAP, ARTEFACT_LOOT_CHEST
from world.procedural_terrain import is_walkable_terrain, GROUND, FOREST, HILL, WATER_SHALLOW, ROCK
from ai.pathfinding import a_star
from typing import Callable

GridPos = Tuple[int, int]


def _terrain_is_walkable(terrain: np.ndarray, r: int, c: int) -> bool:
    # I check if a terrain tile is walkable for pathfinding
    return is_walkable_terrain(terrain[r, c])


def _a_star_terrain(terrain: np.ndarray, start: GridPos, goal: GridPos):
    # I use A* pathfinding to check if artefacts are reachable from the player
    import heapq
    from ai.pathfinding import get_neighbours, heuristic
    
    rows, cols = terrain.shape
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from: dict[GridPos, GridPos] = {}
    g_score = {start: 0}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path
        
        for neighbour in get_neighbours(current, rows, cols):
            nr, nc = neighbour
            if not _terrain_is_walkable(terrain, nr, nc):
                continue
            
            tentative_g = g_score[current] + 1
            
            if neighbour not in g_score or tentative_g < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = tentative_g
                f_score = tentative_g + heuristic(neighbour, goal)
                heapq.heappush(open_set, (f_score, neighbour))
    
    return None


def _get_preferred_terrain(artefact_type: int) -> List[int]:
    # I defined the terrain preferences for the terrain.
    from entities.artefacts import (
        ARTEFACT_HEALTH_POTION, ARTEFACT_COIN, ARTEFACT_WEAPON,
        ARTEFACT_SHIELD, ARTEFACT_TRAP, ARTEFACT_LOOT_CHEST
    )
    
    if artefact_type == ARTEFACT_HEALTH_POTION:
        return [GROUND, FOREST]
    elif artefact_type == ARTEFACT_COIN:
        return [GROUND]
    elif artefact_type == ARTEFACT_WEAPON:
        return [HILL, GROUND]
    elif artefact_type == ARTEFACT_SHIELD:
        return [GROUND, FOREST]
    elif artefact_type == ARTEFACT_TRAP:
        return [GROUND]
    elif artefact_type == ARTEFACT_LOOT_CHEST:
        return [HILL, GROUND]
    else:
        return [GROUND]


def generate_artefacts(terrain: np.ndarray, player_start_tile: GridPos, 
                       tile_size: int, min_per_type: int = 3) -> List[Artefact]:
    # I change this value (e.g. 3, 6, 12, 24) when measuring performance for the report.
    # I generate at least 3 of each artefact type with terrain preferences and accessibility checks
    rows, cols = terrain.shape
    artefacts = []
    occupied_tiles = set()
    
    artefact_types = [
        ARTEFACT_HEALTH_POTION,
        ARTEFACT_COIN,
        ARTEFACT_WEAPON,
        ARTEFACT_SHIELD,
        ARTEFACT_TRAP,
        ARTEFACT_LOOT_CHEST,
    ]
    
    for artefact_type in artefact_types:
        generated = 0
        attempts = 0
        max_attempts = 1000
        preferred_terrain = _get_preferred_terrain(artefact_type)
        
        while generated < min_per_type and attempts < max_attempts:
            attempts += 1
            
            row = random.randint(0, rows - 1)
            col = random.randint(0, cols - 1)
            
            if (row, col) in occupied_tiles:
                continue
            
            tile_id = terrain[row, col]
            
            if not is_walkable_terrain(tile_id):
                continue
            
            # I prefer placing artefacts on their preferred terrain types for seventy percent of the attempts.
            if attempts < max_attempts * 0.7:
                if tile_id not in preferred_terrain:
                    continue
            
            # I validate accessibility using pathfinding so all artefacts are reachable
            target_tile = (row, col)
            path = _a_star_terrain(terrain, player_start_tile, target_tile)
            
            if path is None or len(path) == 0:
                continue
            
            artefact = Artefact(artefact_type, row, col, tile_size)
            artefacts.append(artefact)
            occupied_tiles.add((row, col))
            generated += 1
        
        if generated < min_per_type:
            print(f"Warning: Only generated {generated} of {artefact_type} (target: {min_per_type})")
    
    return artefacts


def get_artefact_paths(terrain: np.ndarray, player_tile: GridPos, 
                      artefacts: List[Artefact]) -> dict:
    # I compute paths from player to each artefact for visualization in Section 2.3
    paths = {}
    for artefact in artefacts:
        artefact_tile = (artefact.row, artefact.col)
        path = _a_star_terrain(terrain, player_tile, artefact_tile)
        if path:
            paths[artefact] = path
    return paths
