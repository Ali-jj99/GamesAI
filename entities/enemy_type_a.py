# This file implements EnemyTypeA which uses A* pathfinding and has aggressive behavior

from entities.enemy_base import EnemyBase


class EnemyTypeA(EnemyBase):
    def __init__(self, x: int, y: int):
        super().__init__(
            x,
            y,
            color=(255, 0, 0),
            size=12,
            speed=1.5
        )
        # I made this enemy type aggressive with long detection range and high bravery
        self.DETECTION_RADIUS = 180
        self.ATTACK_RANGE = 70
        self.LOW_HP_THRESHOLD = 12
        self.HEALED_THRESHOLD = 40
        self.SAFE_DISTANCE = 200
        self.bravery_factor = 0.5
        self.RETREAT_HEALTH_THRESHOLD = self.LOW_HP_THRESHOLD
