# This file implements the player character with movement and terrain-aware speed modifiers

import pygame


class Player:
    def __init__(self, x, y, speed=3, size=12):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        self.color = (0, 0, 255)
        self.health = 100

    def move(self, keys, arena, tile_size: int):
        rows, cols = arena.shape

        # I support both WASD and arrow keys so the game is easier to control
        horiz = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        vert = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(
            keys[pygame.K_w] or keys[pygame.K_UP]
        )

        dx = horiz * self.speed
        dy = vert * self.speed

        # I check which tile the player is standing on to apply speed modifiers
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        tile_x = int(center_x / tile_size)
        tile_y = int(center_y / tile_size)

        # I did this because the player needs to move slower on mud and rain tiles
        speed_factor = 1.0
        if 0 <= tile_y < rows and 0 <= tile_x < cols:
            tile_id = arena[tile_y, tile_x]
            if tile_id == 3:
                speed_factor = 0.5
            elif tile_id == 4:
                speed_factor = 0.7

        dx *= speed_factor
        dy *= speed_factor

        new_x = self.x + dx
        new_y = self.y + dy

        center_x = new_x + self.size / 2
        center_y = new_y + self.size / 2

        tile_x = int(center_x / tile_size)
        tile_y = int(center_y / tile_size)

        # This prevents the player from walking through walls and obstacles
        if 0 <= tile_y < rows and 0 <= tile_x < cols:
            tile_id = arena[tile_y, tile_x]
            if tile_id in [0, 3, 4]:
                self.x = new_x
                self.y = new_y

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            pygame.Rect(self.x, self.y, self.size, self.size),
        )
