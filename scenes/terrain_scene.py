# This file implements the Section 2 scene with procedural terrain and artefacts

import pygame
import sys
import time
import numpy as np
from typing import List, Tuple

from world.procedural_terrain import generate_procedural_terrain, get_terrain_color, \
    WATER_DEEP, WATER_SHALLOW, GROUND, ROCK, FOREST, HILL, GRID_SIZE
from world.artefact_spawner import generate_artefacts, get_artefact_paths
from entities.player import Player
from entities.artefacts import Artefact


def find_walkable_start(terrain: np.ndarray) -> Tuple[int, int]:
    # I find a walkable tile near the center to spawn the player
    rows, cols = terrain.shape
    from world.procedural_terrain import is_walkable_terrain
    
    center_r, center_c = rows // 2, cols // 2
    for offset in range(max(rows, cols)):
        for dr in range(-offset, offset + 1):
            for dc in range(-offset, offset + 1):
                r = center_r + dr
                c = center_c + dc
                if 0 <= r < rows and 0 <= c < cols:
                    if is_walkable_terrain(terrain[r, c]):
                        return (r, c)
    return (0, 0)


class TerrainScene:
    def __init__(self):
        pygame.init()
        
        # --- Performance: terrain generation time (for report) ---
        start_noise = time.perf_counter()
        self.terrain = generate_procedural_terrain(seed=42)
        end_noise = time.perf_counter()
        self.terrain_noise_time = end_noise - start_noise
        print("Terrain noise time (s):", self.terrain_noise_time)
        
        rows, cols = self.terrain.shape
        
        self.tile_size = 12
        self.width = cols * self.tile_size
        self.height = rows * self.tile_size
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Section 2 - Procedural Terrain")
        self.clock = pygame.time.Clock()
        
        player_start_tile = find_walkable_start(self.terrain)
        player_start_x = player_start_tile[1] * self.tile_size + self.tile_size // 2
        player_start_y = player_start_tile[0] * self.tile_size + self.tile_size // 2
        
        self.player = Player(player_start_x, player_start_y, speed=3, size=12)
        self.player_tile = player_start_tile
        
        # --- Performance: artefact placement time (for report) ---
        start_art = time.perf_counter()
        # I generate artefacts with at least 3 of each type for Section 2.2
        self.artefacts = generate_artefacts(
            self.terrain, 
            player_start_tile, 
            self.tile_size,
            min_per_type=3
        )
        end_art = time.perf_counter()
        self.artefact_time = end_art - start_art
        print("Artefact placement time (s):", self.artefact_time)
        
        # --- Performance: total generation time (for report) ---
        self.total_generation_time = self.terrain_noise_time + self.artefact_time
        print("Total generation time (s):", self.total_generation_time)
        
        # I use this toggle to show/hide path visualization for Section 2.3
        self.show_paths = False
        
        self.font = pygame.font.SysFont("Arial", 10)
        self.hud_font = pygame.font.SysFont("Arial", 14)
    
    def update(self, keys):
        # I update player movement and check for artefact collisions
        self._update_player_movement(keys)
        
        # I remove artefacts when the player touches them
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.size, self.player.size)
        self.artefacts = [artefact for artefact in self.artefacts 
                           if not player_rect.colliderect(artefact.rect)]
        
        # I update the player's current tile for path visualization
        center_x = self.player.x + self.player.size / 2
        center_y = self.player.y + self.player.size / 2
        self.player_tile = (
            int(center_y / self.tile_size),
            int(center_x / self.tile_size),
        )
    
    def _update_player_movement(self, keys):
        # I apply terrain-based speed modifiers so the player slows down on forest and hills
        rows, cols = self.terrain.shape
        from world.procedural_terrain import is_walkable_terrain, GROUND, FOREST, HILL
        
        horiz = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        vert = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(
            keys[pygame.K_w] or keys[pygame.K_UP]
        )
        
        center_x = self.player.x + self.player.size / 2
        center_y = self.player.y + self.player.size / 2
        tile_x = int(center_x / self.tile_size)
        tile_y = int(center_y / self.tile_size)
        
        speed_multiplier = 1.0
        if 0 <= tile_y < rows and 0 <= tile_x < cols:
            current_tile = self.terrain[tile_y, tile_x]
            if current_tile == FOREST:
                speed_multiplier = 0.5
            elif current_tile == HILL:
                speed_multiplier = 0.7
            elif current_tile == GROUND:
                speed_multiplier = 1.0
        
        dx = horiz * self.player.speed * speed_multiplier
        dy = vert * self.player.speed * speed_multiplier
        
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        center_x = new_x + self.player.size / 2
        center_y = new_y + self.player.size / 2
        
        tile_x = int(center_x / self.tile_size)
        tile_y = int(center_y / self.tile_size)
        
        # I prevent the player from walking on unwalkable terrain
        if 0 <= tile_y < rows and 0 <= tile_x < cols:
            if is_walkable_terrain(self.terrain[tile_y, tile_x]):
                self.player.x = new_x
                self.player.y = new_y
    
    def draw(self):
        # I draw the terrain, artefacts, player, and optional path visualization
        self.screen.fill((0, 0, 0))
        
        rows, cols = self.terrain.shape
        
        for row in range(rows):
            for col in range(cols):
                tile_id = self.terrain[row, col]
                color = get_terrain_color(tile_id)
                rect = pygame.Rect(
                    col * self.tile_size,
                    row * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                pygame.draw.rect(self.screen, color, rect)
        
        # I draw cyan paths from player to artefacts when the toggle is enabled
        if self.show_paths:
            paths = get_artefact_paths(self.terrain, self.player_tile, self.artefacts)
            path_color = (0, 255, 255)
            
            for artefact, path in paths.items():
                if path and len(path) > 1:
                    path_points = []
                    for r, c in path:
                        x = c * self.tile_size + self.tile_size // 2
                        y = r * self.tile_size + self.tile_size // 2
                        path_points.append((int(x), int(y)))
                    
                    for i in range(len(path_points) - 1):
                        pygame.draw.line(
                            self.screen,
                            path_color,
                            path_points[i],
                            path_points[i + 1],
                            2
                        )
                    
                    for point in path_points:
                        pygame.draw.circle(self.screen, path_color, point, 2)
        
        for artefact in self.artefacts:
            artefact.draw(self.screen)
        
        self.player.draw(self.screen)
        
        self._draw_hud()
    
    def _draw_hud(self):
        # I display artefact count and path visualization status
        artefact_count = len(self.artefacts)
        count_text = self.hud_font.render(f"Artefacts: {artefact_count}", True, (255, 255, 255))
        self.screen.blit(count_text, (10, 10))
        
        if self.show_paths:
            path_text = self.hud_font.render("Paths visible (P to toggle)", True, (0, 255, 255))
            self.screen.blit(path_text, (10, 30))
    
    def run(self):
        # I run the main game loop for Section 2
        running = True
        
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_p:
                        # I toggle path visualization with the P key
                        self.show_paths = not self.show_paths
            
            keys = pygame.key.get_pressed()
            self.update(keys)
            
            self.draw()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
