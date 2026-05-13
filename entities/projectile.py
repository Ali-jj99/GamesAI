# This file implements projectiles that can be fired by the player and enemies

import pygame
import math


class Projectile: 
    def __init__(
        self,
        x,
        y,
        target_x,
        target_y,
        speed=7,
        radius=4,
        color=(255, 0, 0),
        damage: int = 0,
        owner_type: str = "PLAYER",
    ):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        # I store owner_type so the damage model can apply different probabilities for different enemy types
        self.damage = damage
        self.owner_type = owner_type

        # I calculate the direction vector so the projectile moves toward its target
        dx = target_x - x
        dy = target_y - y
        length = math.hypot(dx, dy) or 1.0
        self.vx = (dx / length) * speed
        self.vy = (dy / length) * speed

        self.alive = True

    def update(self, arena, tile_size):
        if not self.alive:
            return

        self.x += self.vx
        self.y += self.vy

        rows, cols = arena.shape

        # This removes projectiles that go off the edge of the map
        if self.x < 0 or self.y < 0 or self.x >= cols * tile_size or self.y >= rows * tile_size:
            self.alive = False
            return

        # This removes projectiles when they hit walls or obstacles
        tile_x = int(self.x / tile_size)
        tile_y = int(self.y / tile_size)

        if arena[tile_y, tile_x] != 0:
            self.alive = False

    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
