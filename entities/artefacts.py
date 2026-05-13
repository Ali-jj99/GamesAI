# This file implements the 6 distinct artefact types for Section 2.2 of the coursework

import pygame
from typing import Tuple

ARTEFACT_HEALTH_POTION = 0
ARTEFACT_COIN = 1
ARTEFACT_WEAPON = 2
ARTEFACT_SHIELD = 3
ARTEFACT_TRAP = 4
ARTEFACT_LOOT_CHEST = 5


class Artefact:
    def __init__(self, artefact_type: int, row: int, col: int, tile_size: int):
        self.type = artefact_type
        self.row = row
        self.col = col
        self.tile_size = tile_size
        
        # I position artefacts at the center of their tile
        self.x = col * tile_size + tile_size // 2
        self.y = row * tile_size + tile_size // 2
        
        self.size = 8
        self.color = self._get_color()
        
        # I create a collision rect so the player can detect when they touch an artefact
        self.rect = pygame.Rect(
            self.x - self.size // 2,
            self.y - self.size // 2,
            self.size,
            self.size
        )
    
    def _get_color(self) -> Tuple[int, int, int]:
        # I assign distinct colors to each artefact type so they're easy to identify
        colors = {
            ARTEFACT_HEALTH_POTION: (255, 0, 0),
            ARTEFACT_COIN: (255, 215, 0),
            ARTEFACT_WEAPON: (139, 69, 19),
            ARTEFACT_SHIELD: (0, 100, 200),
            ARTEFACT_TRAP: (255, 165, 0),
            ARTEFACT_LOOT_CHEST: (160, 82, 45),
        }
        return colors.get(self.type, (255, 255, 255))
    
    def get_name(self) -> str:
        # I provide names for each artefact type for debugging
        names = {
            ARTEFACT_HEALTH_POTION: "Health Potion",
            ARTEFACT_COIN: "Coin",
            ARTEFACT_WEAPON: "Weapon",
            ARTEFACT_SHIELD: "Shield",
            ARTEFACT_TRAP: "Trap",
            ARTEFACT_LOOT_CHEST: "Loot Chest",
        }
        return names.get(self.type, "Unknown")
    
    def draw(self, screen: pygame.Surface):
        # I draw each artefact type with a distinct shape for Section 2.2
        if self.type == ARTEFACT_COIN:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size // 2)
            pygame.draw.circle(screen, (200, 150, 0), (int(self.x), int(self.y)), self.size // 2 - 1)
        elif self.type == ARTEFACT_HEALTH_POTION:
            rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, (200, 0, 0), rect, 1)
        elif self.type == ARTEFACT_LOOT_CHEST:
            rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, (100, 50, 25), rect, 2)
        elif self.type == ARTEFACT_TRAP:
            half = self.size // 2
            pygame.draw.line(screen, self.color, 
                           (self.x - half, self.y - half),
                           (self.x + half, self.y + half), 2)
            pygame.draw.line(screen, self.color,
                           (self.x - half, self.y + half),
                           (self.x + half, self.y - half), 2)
        else:
            rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)
