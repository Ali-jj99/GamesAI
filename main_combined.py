# This file implements the combined model for Section 3 of the coursework, combining terrain, combat, and probabilistic damage

import sys
from typing import Tuple, List

import pygame
import numpy as np

from world.arena_generator import EMPTY, WALL, OBSTACLE, MUD, RAIN
from world.procedural_terrain import (
    generate_procedural_terrain,
    get_terrain_color,
    is_walkable_terrain,
    WATER_DEEP,
    WATER_SHALLOW,
    GROUND,
    ROCK,
    FOREST,
    HILL,
)
from entities.player import Player
from entities.projectile import Projectile
from entities.enemy_type_a import EnemyTypeA
from entities.enemy_type_b import EnemyTypeB
from entities.artefacts import Artefact
from core.damage_models import (
    calculate_player_bullet_damage,
    calculate_enemy_ranged_damage_for_type,
    calculate_enemy_melee_damage,
)
from world.artefact_spawner import generate_artefacts


GridPos = Tuple[int, int]


def _terrain_to_arena_layer(terrain: np.ndarray) -> np.ndarray:
    # I convert Section 2 terrain into Section 1 arena format so I can reuse the same pathfinding and movement code
    rows, cols = terrain.shape
    arena = np.zeros((rows, cols), dtype=int)

    for r in range(rows):
        for c in range(cols):
            t = terrain[r, c]
            # I map unwalkable terrain to WALL so pathfinding treats them as blocked
            if t in (WATER_DEEP, WATER_SHALLOW, ROCK):
                arena[r, c] = WALL
            # I map walkable terrain to EMPTY, MUD, or RAIN so movement slowdowns work
            elif t == GROUND:
                arena[r, c] = EMPTY
            elif t == FOREST:
                arena[r, c] = MUD
            elif t == HILL:
                arena[r, c] = RAIN
            else:
                arena[r, c] = WALL

    return arena


def _find_walkable_start(terrain: np.ndarray) -> GridPos:
    # I find a walkable tile near the center to spawn the player
    rows, cols = terrain.shape
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


def _spawn_enemies_on_terrain(
    terrain: np.ndarray,
    arena_layer: np.ndarray,
    tile_size: int,
    player_start: GridPos,
    num_type_a: int = 2,
    num_type_b: int = 2,
) -> List[object]:
    # I spawn enemies on walkable terrain tiles, ensuring they don't overlap
    rows, cols = terrain.shape
    enemies: List[object] = []
    occupied_tiles = {player_start}

    def _pick_random_walkable_tile() -> GridPos:
        import random

        for _ in range(1000):
            r = random.randint(0, rows - 1)
            c = random.randint(0, cols - 1)
            if (r, c) in occupied_tiles:
                continue
            if not is_walkable_terrain(terrain[r, c]):
                continue
            # I check the arena layer too so enemies only spawn where pathfinding works
            if arena_layer[r, c] not in (EMPTY, MUD, RAIN):
                continue
            return (r, c)
        return (rows // 2, cols // 2)

    # I spawn EnemyTypeA which uses A* pathfinding
    for _ in range(num_type_a):
        tile = _pick_random_walkable_tile()
        occupied_tiles.add(tile)
        x = tile[1] * tile_size
        y = tile[0] * tile_size
        enemies.append(EnemyTypeA(x, y))

    # I spawn EnemyTypeB which uses BFS pathfinding
    for _ in range(num_type_b):
        tile = _pick_random_walkable_tile()
        occupied_tiles.add(tile)
        x = tile[1] * tile_size
        y = tile[0] * tile_size
        enemies.append(EnemyTypeB(x, y))

    return enemies


def run_combined_scene():
    # This part runs the combined scene that integrates Section 1 combat with Section 2 terrain
    pygame.init()

    terrain = generate_procedural_terrain(seed=42)
    arena = _terrain_to_arena_layer(terrain)  # I convert terrain to arena format so pathfinding and movement work correctly
    rows, cols = terrain.shape

    tile_size = 12
    width = cols * tile_size
    height = rows * tile_size

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Game AI - Combined Terrain + Combat")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 12)
    hud_font = pygame.font.SysFont("Arial", 18)

    player_start_tile = _find_walkable_start(terrain)
    player_start_x = player_start_tile[1] * tile_size
    player_start_y = player_start_tile[0] * tile_size
    player = Player(player_start_x, player_start_y, speed=3, size=12)

    enemies = _spawn_enemies_on_terrain(
        terrain,
        arena,
        tile_size,
        player_start_tile,
        num_type_a=2,
        num_type_b=2,
    )

    # I generate artefacts from Section 2 so the combined scene has collectible items
    artefacts: List[Artefact] = generate_artefacts(
        terrain,
        player_start_tile,
        tile_size,
        min_per_type=3
    )

    projectiles: List[Projectile] = []
    enemy_projectiles: List[Projectile] = []

    debug_mode = False
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key in (pygame.K_TAB, pygame.K_F1):
                    debug_mode = not debug_mode

            # I allow the player to shoot projectiles by clicking the mouse
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                proj = Projectile(
                    player.x + player.size / 2,
                    player.y + player.size / 2,
                    mouse_x,
                    mouse_y,
                )
                projectiles.append(proj)

        keys = pygame.key.get_pressed()
        # I reuse Section 1 movement so the player slows down on MUD/RAIN equivalent tiles
        player.move(keys, arena, tile_size)

        # I remove artefacts when the player touches them, same as Section 2
        player_rect = pygame.Rect(player.x, player.y, player.size, player.size)
        artefacts = [artefact for artefact in artefacts 
                     if not player_rect.colliderect(artefact.rect)]

        for proj in projectiles:
            proj.update(arena, tile_size)
        projectiles = [p for p in projectiles if p.alive]

        for proj in enemy_projectiles:
            proj.update(arena, tile_size)
        enemy_projectiles = [p for p in enemy_projectiles if p.alive]

        # I track occupied tiles so enemies don't try to move into the same space
        initial_occupied_tiles = {}
        for i, enemy in enumerate(enemies):
            if enemy.health > 0:
                enemy_tile = enemy.pixel_to_tile(tile_size)
                initial_occupied_tiles[i] = enemy_tile

        # I update enemies so they use their FSM states and pathfinding
        player_center = (player.x + player.size / 2, player.y + player.size / 2)
        for i, enemy in enumerate(enemies):
            if enemy.health <= 0:
                continue

            other_occupied = set()
            for j, other_enemy in enumerate(enemies):
                if i != j and other_enemy.health > 0:
                    other_tile = other_enemy.pixel_to_tile(tile_size)
                    other_occupied.add(other_tile)

            enemy.update(arena, player_center, tile_size, other_occupied)

            # I allow enemies to shoot when they're in CHASE or ATTACK state
            enemy_proj = enemy.shoot_at_player(player_center)
            if enemy_proj is not None:
                enemy_projectiles.append(enemy_proj)

        # I handle player bullets hitting enemies with probability-based damage
        for proj in projectiles:
            if not proj.alive:
                continue
            for enemy in enemies:
                if enemy.health <= 0:
                    continue

                enemy_cx = enemy.x + enemy.size / 2
                enemy_cy = enemy.y + enemy.size / 2
                dx = proj.x - enemy_cx
                dy = proj.y - enemy_cy
                dist_sq = dx * dx + dy * dy
                hit_radius = proj.radius + enemy.size / 2

                if dist_sq <= hit_radius * hit_radius:
                    # I use probability-based damage so different enemy types take different damage
                    damage = calculate_player_bullet_damage(enemy)
                    enemy.take_damage(damage)
                    proj.alive = False
                    break

        # I handle enemy bullets hitting the player with asymmetric probability-based damage
        for proj in enemy_projectiles:
            if not proj.alive:
                continue

            player_cx = player.x + player.size / 2
            player_cy = player.y + player.size / 2
            dx = proj.x - player_cx
            dy = proj.y - player_cy
            dist_sq = dx * dx + dy * dy
            hit_radius = proj.radius + player.size / 2

            if dist_sq <= hit_radius * hit_radius:
                # I check owner_type so EnemyTypeA and EnemyTypeB have different hit chances
                damage = calculate_enemy_ranged_damage_for_type(getattr(proj, "owner_type", "UNKNOWN"))
                if damage > 0:
                    player.health = max(0, player.health - damage)
                proj.alive = False

        projectiles = [p for p in projectiles if p.alive]
        enemy_projectiles = [p for p in enemy_projectiles if p.alive]
        enemies = [e for e in enemies if e.health > 0]

        # I handle melee attacks when enemies get very close to the player
        MELEE_ATTACK_RADIUS = 20
        for enemy in enemies:
            if enemy.state != "CHASE" and enemy.state != "ATTACK":
                continue

            enemy_cx = enemy.x + enemy.size / 2
            enemy_cy = enemy.y + enemy.size / 2
            dx = enemy_cx - player_center[0]
            dy = enemy_cy - player_center[1]
            dist_sq = dx * dx + dy * dy

            if dist_sq <= MELEE_ATTACK_RADIUS * MELEE_ATTACK_RADIUS and enemy.attack_cooldown == 0:
                # I use probability-based melee damage so there's a chance to miss
                melee_damage = calculate_enemy_melee_damage(enemy)
                if melee_damage > 0:
                    player.health = max(0, player.health - melee_damage)
                enemy.attack_cooldown = 30

        screen.fill((0, 0, 0))

        # I draw the procedural terrain using Section 2 colors
        for r in range(rows):
            for c in range(cols):
                tile_id = terrain[r, c]
                color = get_terrain_color(tile_id)
                rect = pygame.Rect(c * tile_size, r * tile_size, tile_size, tile_size)
                pygame.draw.rect(screen, color, rect)

        # I draw artefacts on top of terrain
        for artefact in artefacts:
            artefact.draw(screen)

        player.draw(screen)

        for proj in projectiles:
            proj.draw(screen)
        for proj in enemy_projectiles:
            proj.draw(screen)

        for enemy in enemies:
            enemy.draw(screen, font)

        hp_text = hud_font.render(f"HP: {player.health}", True, (0, 0, 0))
        screen.blit(hp_text, (10, 10))

        mode_text = hud_font.render("Combined Terrain + FSM + Probabilistic Damage", True, (0, 0, 0))
        screen.blit(mode_text, (10, 30))

        if debug_mode:
            dbg = hud_font.render("DEBUG: TAB/F1 to toggle", True, (255, 255, 0))
            screen.blit(dbg, (10, height - 25))

        if player.health <= 0:
            go_text = hud_font.render("GAME OVER", True, (200, 0, 0))
            text_rect = go_text.get_rect(center=(width // 2, height // 2))
            screen.blit(go_text, text_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_combined_scene()
