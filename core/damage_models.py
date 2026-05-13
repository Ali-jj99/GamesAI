# This file implements probability-based damage models for Extended Behavioural Modelling 1 of the coursework

import random
from typing import Any


def _get_enemy_type_name(enemy: Any) -> str:
    # I use this helper to get the enemy type name without importing the classes directly
    return getattr(enemy, "__class__", type(enemy)).__name__


def calculate_player_bullet_damage(enemy: Any) -> int:
    # I implemented asymmetric damage distributions so EnemyTypeA and EnemyTypeB feel different in combat
    enemy_type = _get_enemy_type_name(enemy)
    r = random.random()

    if enemy_type == "EnemyTypeA":
        # I made EnemyTypeA have a 60% chance for normal hits, 20% for criticals, 20% for grazes
        if r < 0.6:
            return random.randint(15, 20)
        elif r < 0.8:
            return random.randint(25, 30)
        else:
            return random.randint(5, 10)

    if enemy_type == "EnemyTypeB":
        # I made EnemyTypeB have different probabilities to create asymmetric combat
        if r < 0.5:
            return random.randint(12, 18)
        elif r < 0.75:
            return random.randint(22, 30)
        else:
            return random.randint(4, 9)

    return 20


def calculate_enemy_ranged_damage_for_type(owner_type: str) -> int:
    # I implemented asymmetric hit chances so EnemyTypeA is more accurate but EnemyTypeB does more damage when it hits
    r = random.random()

    if owner_type == "EnemyTypeA":
        # I made EnemyTypeA have 70% hit chance with moderate damage
        if r < 0.7:
            return random.randint(6, 10)
        return 0

    if owner_type == "EnemyTypeB":
        # I made EnemyTypeB have 50% hit chance but higher damage when it hits
        if r < 0.5:
            return random.randint(10, 18)
        return 0

    if r < 0.6:
        return random.randint(5, 10)
    return 0


def calculate_enemy_melee_damage(enemy: Any) -> int:
    # I implemented different melee damage distributions for each enemy type
    enemy_type = _get_enemy_type_name(enemy)
    r = random.random()

    if enemy_type == "EnemyTypeA":
        # I made EnemyTypeA have 80% hit chance with moderate damage
        if r < 0.8:
            return random.randint(4, 8)
        return 0

    if enemy_type == "EnemyTypeB":
        # I made EnemyTypeB have 55% hit chance but higher damage potential
        if r < 0.55:
            return random.randint(8, 14)
        return 0

    if r < 0.7:
        return random.randint(3, 6)
    return 0
