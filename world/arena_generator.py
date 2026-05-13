# This file generates the fixed combat arena for Section 1 of the coursework

import numpy as np

EMPTY = 0
WALL = 1
OBSTACLE = 2
MUD = 3
RAIN = 4

GRID_SIZE = 60


def generate_arena():
    # I create a maze-like arena with multiple rooms and paths for Section 1.1
    arena = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

    arena[0, :] = WALL
    arena[-1, :] = WALL
    arena[:, 0] = WALL
    arena[:, -1] = WALL

    # I create four rooms in the corners with internal walls
    r1_top, r1_bottom = 3, 18
    r1_left, r1_right = 3, 18
    
    arena[r1_top:r1_bottom, r1_left] = WALL
    arena[r1_top:r1_bottom, r1_right] = WALL
    arena[r1_top, r1_left:r1_right] = WALL
    arena[r1_bottom, r1_left:r1_right + 1] = WALL
    
    arena[8:10, r1_left + 1:r1_left + 5] = WALL
    arena[12:14, r1_left + 8:r1_right] = WALL
    
    arena[r1_top + 1:r1_bottom, r1_left + 1:r1_right] = EMPTY

    r2_top, r2_bottom = 3, 18
    r2_left, r2_right = 32, 47
    
    arena[r2_top:r2_bottom, r2_left] = WALL
    arena[r2_top:r2_bottom, r2_right] = WALL
    arena[r2_top, r2_left:r2_right] = WALL
    arena[r2_bottom, r2_left:r2_right + 1] = WALL
    
    arena[10:12, r2_left + 1:r2_left + 6] = WALL
    
    arena[r2_top + 1:r2_bottom, r2_left + 1:r2_right] = EMPTY

    r3_top, r3_bottom = 32, 47
    r3_left, r3_right = 3, 18
    
    arena[r3_top:r3_bottom, r3_left] = WALL
    arena[r3_top:r3_bottom, r3_right] = WALL
    arena[r3_top, r3_left:r3_right] = WALL
    arena[r3_bottom, r3_left:r3_right + 1] = WALL
    
    arena[r3_top + 5:r3_top + 7, r3_left + 1:r3_left + 8] = WALL
    
    arena[r3_top + 1:r3_bottom, r3_left + 1:r3_right] = EMPTY

    r4_top, r4_bottom = 32, 47
    r4_left, r4_right = 32, 47
    
    arena[r4_top:r4_bottom, r4_left] = WALL
    arena[r4_top:r4_bottom, r4_right] = WALL
    arena[r4_top, r4_left:r4_right] = WALL
    arena[r4_bottom, r4_left:r4_right + 1] = WALL
    
    arena[r4_top + 3:r4_top + 5, r4_left + 1:r4_right] = WALL
    
    arena[r4_top + 1:r4_bottom, r4_left + 1:r4_right] = EMPTY

    # I create multiple doorways between rooms so there are multiple pathfinding routes
    arena[r1_bottom, 8:11] = EMPTY
    arena[r1_bottom, 13:16] = EMPTY
    arena[10:13, r1_right] = EMPTY
    
    arena[r2_bottom, 35:38] = EMPTY
    arena[r2_bottom, 41:44] = EMPTY
    arena[10:13, r2_left] = EMPTY
    
    arena[r3_top, 8:11] = EMPTY
    arena[r3_top, 13:16] = EMPTY
    arena[38:41, r3_right] = EMPTY
    
    arena[r4_top, 35:38] = EMPTY
    arena[r4_top, 41:44] = EMPTY
    arena[38:41, r4_left] = EMPTY

    # I create connecting paths in the center area
    arena[23:26, 20:30] = EMPTY
    arena[20:30, 23:26] = EMPTY
    
    arena[18:22, 15:20] = EMPTY
    arena[18:22, 30:35] = EMPTY
    arena[28:32, 15:20] = EMPTY
    arena[28:32, 30:35] = EMPTY

    # I place random obstacles in the central area to make pathfinding more interesting
    np.random.seed(42)
    obstacle_count = 80
    
    blocked_tiles = set()
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if (row < 20 or row > 30 or col < 20 or col > 30) and \
               not (3 <= row <= 18 and 3 <= col <= 18) and \
               not (3 <= row <= 18 and 32 <= col <= 47) and \
               not (32 <= row <= 47 and 3 <= col <= 18) and \
               not (32 <= row <= 47 and 32 <= col <= 47):
                blocked_tiles.add((row, col))
    
    door_tiles = [
        (r1_bottom, 8), (r1_bottom, 9), (r1_bottom, 10), (r1_bottom, 13), (r1_bottom, 14), (r1_bottom, 15),
        (r2_bottom, 35), (r2_bottom, 36), (r2_bottom, 37), (r2_bottom, 41), (r2_bottom, 42), (r2_bottom, 43),
        (r3_top, 8), (r3_top, 9), (r3_top, 10), (r3_top, 13), (r3_top, 14), (r3_top, 15),
        (r4_top, 35), (r4_top, 36), (r4_top, 37), (r4_top, 41), (r4_top, 42), (r4_top, 43),
        (10, r1_right), (11, r1_right), (12, r1_right),
        (10, r2_left), (11, r2_left), (12, r2_left),
        (38, r3_right), (39, r3_right), (40, r3_right),
        (38, r4_left), (39, r4_left), (40, r4_left),
    ]
    blocked_tiles.update(door_tiles)

    for _ in range(obstacle_count):
        y = np.random.randint(1, GRID_SIZE - 1)
        x = np.random.randint(1, GRID_SIZE - 1)
        
        if (y, x) in blocked_tiles:
            continue
        
        if arena[y, x] == EMPTY:
            arena[y, x] = OBSTACLE

    for row, col in door_tiles:
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            arena[row, col] = EMPTY

    # I add MUD and RAIN tiles so players and enemies slow down on certain terrain
    mud_zones = [
        (20, 20, 5, 5),
        (25, 25, 4, 4),
        (35, 15, 6, 6),
        (15, 35, 5, 5),
    ]
    
    for r, c, h, w in mud_zones:
        for dr in range(h):
            for dc in range(w):
                row = r + dr
                col = c + dc
                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                    if arena[row, col] == EMPTY:
                        arena[row, col] = MUD
    
    rain_zones = [
        (22, 22, 4, 4),
        (30, 30, 5, 5),
        (40, 20, 6, 4),
        (20, 40, 4, 6),
        (45, 45, 5, 5),
    ]
    
    for r, c, h, w in rain_zones:
        for dr in range(h):
            for dc in range(w):
                row = r + dr
                col = c + dc
                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                    if arena[row, col] == EMPTY:
                        arena[row, col] = RAIN

    return arena
