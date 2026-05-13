# This file implements EnemyTypeB which uses BFS pathfinding and has cautious behavior

from entities.enemy_base import EnemyBase
from ai.pathfinding import bfs_shortest_path


class EnemyTypeB(EnemyBase):
    def __init__(self, x: int, y: int):
        super().__init__(
            x,
            y,
            color=(200, 0, 200),
            size=12,
            speed=1.2
        )
        # I made this enemy type cautious with shorter detection range and low bravery
        self.DETECTION_RADIUS = 120
        self.ATTACK_RANGE = 50
        self.LOW_HP_THRESHOLD = 18
        self.HEALED_THRESHOLD = 45
        self.SAFE_DISTANCE = 180
        self.bravery_factor = 0.1
        self.RETREAT_HEALTH_THRESHOLD = self.LOW_HP_THRESHOLD

    def _get_path(self, arena, start_tile, goal_tile):
        # I override the pathfinding method to use BFS instead of A* for Section 1.3
        return bfs_shortest_path(arena, start_tile, goal_tile)
