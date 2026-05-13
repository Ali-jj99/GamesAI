# This file implements advanced procedural terrain generation for Section 2 of the coursework

import numpy as np
import math

WATER_DEEP = 0
WATER_SHALLOW = 1
GROUND = 2
ROCK = 3
FOREST = 4
HILL = 5

GRID_SIZE = 64


def simple_noise(x: float, y: float, seed: int = 0) -> float:
    # I use a simple hash function to generate pseudo random noise values
    n = int(x * 73.0 + y * 37.0 + seed * 101.0)
    n = (n << 13) ^ n
    return (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0) * 0.5 + 0.5


def smooth_noise(x: float, y: float, seed: int = 0) -> float:
    # I use bilinear interpolation to smooth the noise values
    x_int = int(x)
    y_int = int(y)
    x_frac = x - x_int
    y_frac = y - y_int
    
    v1 = simple_noise(x_int, y_int, seed)
    v2 = simple_noise(x_int + 1, y_int, seed)
    v3 = simple_noise(x_int, y_int + 1, seed)
    v4 = simple_noise(x_int + 1, y_int + 1, seed)
    
    i1 = v1 * (1 - x_frac) + v2 * x_frac
    i2 = v3 * (1 - x_frac) + v4 * x_frac
    
    return i1 * (1 - y_frac) + i2 * y_frac


def fractal_noise(x: float, y: float, octaves: int = 4, seed: int = 0) -> float:
    # I combine multiple octaves of noise to create fractal patterns for Section 2.1
    value = 0.0
    amplitude = 1.0
    frequency = 0.01
    max_value = 0.0
    
    for _ in range(octaves):
        value += smooth_noise(x * frequency, y * frequency, seed) * amplitude
        max_value += amplitude
        amplitude *= 0.5
        frequency *= 2.0
    
    return value / max_value


def generate_procedural_terrain(seed: int = 42) -> np.ndarray:
    # This part generates terrain using layered noise for Section 2.1 of the coursework
    terrain = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    
    # I generate separate height and moisture maps using fractal noise
    height_map = np.zeros((GRID_SIZE, GRID_SIZE))
    moisture_map = np.zeros((GRID_SIZE, GRID_SIZE))
    
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            # I use different seeds for height and moisture to create varied terrain
            height_map[row, col] = fractal_noise(col, row, octaves=4, seed=seed)
            moisture_map[row, col] = fractal_noise(col, row, octaves=3, seed=seed + 1000)
    
    # I normalize the maps to 0-1 range so I can use thresholds
    height_map = (height_map - height_map.min()) / (height_map.max() - height_map.min() + 0.001)
    moisture_map = (moisture_map - moisture_map.min()) / (moisture_map.max() - moisture_map.min() + 0.001)
    
    # I assign terrain types based on height and moisture values
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            height = height_map[row, col]
            moisture = moisture_map[row, col]
            
            # I use height thresholds to create different terrain types
            if height < 0.25:
                if height < 0.15:
                    terrain[row, col] = WATER_DEEP
                else:
                    terrain[row, col] = WATER_SHALLOW
            elif height < 0.35:
                terrain[row, col] = GROUND
            elif height < 0.55:
                # I use moisture to decide between forest and ground.
                if moisture > 0.6:
                    terrain[row, col] = FOREST
                else:
                    terrain[row, col] = GROUND
            elif height < 0.75:
                terrain[row, col] = HILL
            else:
                terrain[row, col] = ROCK
    
    return terrain

def is_walkable_terrain(tile_id: int) -> bool:
    # I check if a terrain tile can be walked on by the player
    return tile_id in [GROUND, FOREST, HILL]


def get_terrain_color(tile_id: int) -> tuple:
    # I assign distinct colors to each terrain type so they're visually clear
    colors = {
        WATER_DEEP: (20, 50, 120),
        WATER_SHALLOW: (50, 100, 200),
        GROUND: (100, 150, 80),
        ROCK: (100, 100, 100),
        FOREST: (30, 80, 40),
        HILL: (120, 100, 60),
    }
    return colors.get(tile_id, (0, 0, 0))
