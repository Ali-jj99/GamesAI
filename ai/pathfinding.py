# This file implements A* and BFS pathfinding algorithms for Section 1.3 of the coursework

import heapq
from collections import deque
from typing import List, Tuple, Optional

GridPos = Tuple[int, int]


def heuristic(a: GridPos, b: GridPos) -> float:
    # I use Manhattan distance as the heuristic for A* pathfinding
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbours(pos: GridPos, rows: int, cols: int) -> List[GridPos]:
    # This returns the four adjacent tiles (up, down, left, right) that are within bounds
    r, c = pos
    neighbours = [
        (r - 1, c),
        (r + 1, c),
        (r, c - 1),
        (r, c + 1),
    ]
    return [
        (nr, nc)
        for nr, nc in neighbours
        if 0 <= nr < rows and 0 <= nc < cols
    ]


def is_walkable(arena, r: int, c: int) -> bool:
    # This checks if a tile can be walked on (EMPTY, MUD, RAIN are walkable)
    tile_id = arena[r, c]
    return tile_id in [0, 3, 4]


def get_tile_cost(arena, r: int, c: int) -> float:
    # I assign different costs to different terrain types so pathfinding avoids slow tiles when possible
    tile_id = arena[r, c]
    if tile_id == 0:
        return 1.0
    elif tile_id == 3:
        return 3.0
    elif tile_id == 4:
        return 2.0
    else:
        return 999.0


def a_star(arena, start: GridPos, goal: GridPos) -> Optional[List[GridPos]]:
    # This implements A* pathfinding for EnemyTypeA as required by Section 1.3
    rows, cols = arena.shape
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from: dict[GridPos, GridPos] = {}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            # I reconstruct the path by following the came_from links back to the start
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        for neighbour in get_neighbours(current, rows, cols):
            nr, nc = neighbour
            if not is_walkable(arena, nr, nc):
                continue

            # I use terrain costs so the pathfinding prefers faster routes
            move_cost = get_tile_cost(arena, nr, nc)
            tentative_g = g_score[current] + move_cost

            if neighbour not in g_score or tentative_g < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = tentative_g
                f_score = tentative_g + heuristic(neighbour, goal)
                heapq.heappush(open_set, (f_score, neighbour))

    return None


def bfs_shortest_path(arena, start: GridPos, goal: GridPos) -> Optional[List[GridPos]]:
    # This implements cost-aware BFS pathfinding for EnemyTypeB as required by Section 1.3
    rows, cols = arena.shape
    
    if not is_walkable(arena, start[0], start[1]) or not is_walkable(arena, goal[0], goal[1]):
        return None
    
    # I use a priority queue so the algorithm respects terrain costs
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    visited = {start}
    came_from: dict[GridPos, GridPos] = {}
    g_score = {start: 0}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == goal:
            # I reconstruct the path by following the came_from links
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path
        
        for neighbour in get_neighbours(current, rows, cols):
            nr, nc = neighbour
            if not is_walkable(arena, nr, nc):
                continue
            
            # I use terrain costs so expensive tiles are avoided when possible
            move_cost = get_tile_cost(arena, nr, nc)
            tentative_g = g_score[current] + move_cost
            
            if neighbour not in g_score or tentative_g < g_score[neighbour]:
                g_score[neighbour] = tentative_g
                came_from[neighbour] = current
                heapq.heappush(open_set, (tentative_g, neighbour))
    
    return None
