# This file implements Section 1 of the coursework: fixed combat arena with NPCs, FSM states, and probability-based damage

import sys
import pygame

from world.arena_generator import generate_arena, EMPTY, WALL, OBSTACLE, MUD, RAIN
from entities.player import Player
from entities.projectile import Projectile
from entities.enemy_type_a import EnemyTypeA
from entities.enemy_type_b import EnemyTypeB
from ai.pathfinding import a_star, bfs_shortest_path
from core.damage_models import (
    calculate_player_bullet_damage,
    calculate_enemy_ranged_damage_for_type,
    calculate_enemy_melee_damage,
)

pygame.init()

arena = generate_arena()
rows, cols = arena.shape

TILE_SIZE = 14
WIDTH = cols * TILE_SIZE
HEIGHT = rows * TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game AI - Section 1 Arena")
clock = pygame.time.Clock()

# I added these colors so different terrain types are visually distinct
COLORS = {
    EMPTY: (220, 220, 230),
    WALL: (40, 40, 50),
    OBSTACLE: (139, 69, 19),
    MUD: (110, 80, 40),
    RAIN: (190, 200, 230),
}

font = pygame.font.SysFont("Arial", 12)
hud_font = pygame.font.SysFont("Arial", 18)

# This part spawns the player at a fixed starting position
player_start_x = 10 * TILE_SIZE
player_start_y = 10 * TILE_SIZE
player = Player(player_start_x, player_start_y, speed=3, size=12)

projectiles = []
enemy_projectiles = []

# I spawn two EnemyTypeA (using A* pathfinding) and two EnemyTypeB (using BFS pathfinding) to demonstrate both algorithms
enemies = [
    EnemyTypeA(35 * TILE_SIZE, 35 * TILE_SIZE),
    EnemyTypeA(40 * TILE_SIZE, 10 * TILE_SIZE),
    EnemyTypeB(15 * TILE_SIZE, 35 * TILE_SIZE),
    EnemyTypeB(45 * TILE_SIZE, 15 * TILE_SIZE),
]

debug_mode = False
running = True

while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # I added this toggle so I can visualize pathfinding during development
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB or event.key == pygame.K_F1:
                debug_mode = not debug_mode

        # This allows the player to shoot projectiles by clicking the mouse
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
    player.move(keys, arena, TILE_SIZE)

    # This part updates all projectiles and removes ones that hit walls or went off-screen
    for proj in projectiles:
        proj.update(arena, TILE_SIZE)
    projectiles = [p for p in projectiles if p.alive]
    
    for proj in enemy_projectiles:
        proj.update(arena, TILE_SIZE)
    enemy_projectiles = [p for p in enemy_projectiles if p.alive]

    # I track occupied tiles so enemies don't try to move into the same space as other enemies
    initial_occupied_tiles = {}
    for i, enemy in enumerate(enemies):
        if enemy.health > 0:
            enemy_tile = enemy.pixel_to_tile(TILE_SIZE)
            initial_occupied_tiles[i] = enemy_tile
    
    # This part updates each enemy's FSM state and makes them chase or retreat based on their AI
    player_center = (player.x + player.size / 2, player.y + player.size / 2)
    for i, enemy in enumerate(enemies):
        if enemy.health <= 0:
            continue
            
        # I exclude this enemy's own tile from the occupied set so it can move
        other_occupied = set()
        for j, other_enemy in enumerate(enemies):
            if i != j and other_enemy.health > 0:
                other_tile = other_enemy.pixel_to_tile(TILE_SIZE)
                other_occupied.add(other_tile)
        
        enemy.update(arena, player_center, TILE_SIZE, other_occupied)
        
        # This allows enemies to shoot at the player when they are in CHASE or ATTACK state
        enemy_proj = enemy.shoot_at_player(player_center)
        if enemy_proj is not None:
            enemy_projectiles.append(enemy_proj)

    # This part handles player bullets hitting enemies with probability-based damage
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
                # I use probability-based damage so different enemy types take different amounts of damage
                damage = calculate_player_bullet_damage(enemy)
                enemy.take_damage(damage)
                proj.alive = False
                break

    # This part handles enemy bullets hitting the player with asymmetric probability-based damage
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
            # I check the owner_type so EnemyTypeA and EnemyTypeB have different hit chances and damage
            damage = calculate_enemy_ranged_damage_for_type(getattr(proj, "owner_type", "UNKNOWN"))
            if damage > 0:
                player.health = max(0, player.health - damage)
            proj.alive = False
    
    projectiles = [p for p in projectiles if p.alive]
    enemy_projectiles = [p for p in enemy_projectiles if p.alive]
    enemies = [e for e in enemies if e.health > 0]

    # This part handles melee attacks when enemies get very close to the player
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
            # I use probability-based melee damage so there's a chance to miss or do different damage
            melee_damage = calculate_enemy_melee_damage(enemy)
            if melee_damage > 0:
                player.health = max(0, player.health - melee_damage)
            enemy.attack_cooldown = 30

    # This part draws the arena tiles with different colors for different terrain types
    for row in range(rows):
        for col in range(cols):
            tile_id = arena[row, col]
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)

            base_color = COLORS.get(tile_id, (0, 0, 0))
            pygame.draw.rect(screen, base_color, rect)

            # I added extra visual details for MUD and RAIN tiles so they look more distinct
            if tile_id == MUD:
                inner_color = (80, 55, 30)
                inset = TILE_SIZE // 6
                inner_rect = pygame.Rect(
                    rect.x + inset,
                    rect.y + inset,
                    TILE_SIZE - 2 * inset,
                    TILE_SIZE - 2 * inset,
                )
                pygame.draw.ellipse(screen, inner_color, inner_rect)

                dot_radius = max(2, TILE_SIZE // 6)
                pygame.draw.circle(
                    screen,
                    (60, 40, 20),
                    (rect.centerx - dot_radius, rect.centery + dot_radius // 2),
                    dot_radius,
                )
                pygame.draw.circle(
                    screen,
                    (70, 50, 25),
                    (rect.centerx + dot_radius, rect.centery - dot_radius // 2),
                    dot_radius - 1,
                )

            elif tile_id == RAIN:
                puddle_color = (220, 230, 255)
                small_w = max(3, TILE_SIZE // 3)
                small_h = max(2, TILE_SIZE // 4)

                puddle1 = pygame.Rect(
                    rect.x + TILE_SIZE // 6,
                    rect.y + TILE_SIZE // 4,
                    small_w,
                    small_h,
                )
                puddle2 = pygame.Rect(
                    rect.x + TILE_SIZE // 2,
                    rect.y + TILE_SIZE // 2,
                    small_w,
                    small_h,
                )
                pygame.draw.ellipse(screen, puddle_color, puddle1)
                pygame.draw.ellipse(screen, puddle_color, puddle2)

    player.draw(screen)

    for proj in projectiles:
        proj.draw(screen)
    
    for proj in enemy_projectiles:
        proj.draw(screen)

    # This part draws each enemy and shows their ID, health, and current FSM state
    for enemy in enemies:
        enemy.draw(screen, font)
        
        # I added this debug visualization to show pathfinding paths during development
        if debug_mode:
            player_tile = (int((player.y + player.size / 2) / TILE_SIZE),
                          int((player.x + player.size / 2) / TILE_SIZE))
            enemy_tile = enemy.pixel_to_tile(TILE_SIZE)
            
            # This shows the path from enemy to player using A* or BFS depending on enemy type
            if isinstance(enemy, EnemyTypeA):
                path = a_star(arena, enemy_tile, player_tile)
            else:
                path = bfs_shortest_path(arena, enemy_tile, player_tile)
            
            if path:
                path_slice = path[1:6]
                for i, (r, c) in enumerate(path_slice):
                    x = c * TILE_SIZE + TILE_SIZE // 2
                    y = r * TILE_SIZE + TILE_SIZE // 2
                    pygame.draw.circle(screen, (0, 255, 0), (int(x), int(y)), 3)
                    if i + 1 < len(path_slice):
                        next_r, next_c = path_slice[i + 1]
                        next_x = next_c * TILE_SIZE + TILE_SIZE // 2
                        next_y = next_r * TILE_SIZE + TILE_SIZE // 2
                        pygame.draw.line(screen, (0, 200, 0), (int(x), int(y)), 
                                         (int(next_x), int(next_y)), 1)
            
            debug_text = font.render(f"Tile: {enemy_tile}", True, (255, 255, 0))
            screen.blit(debug_text, (enemy.x, enemy.y - 28))

    if debug_mode:
        player_tile = (int((player.y + player.size / 2) / TILE_SIZE),
                      int((player.x + player.size / 2) / TILE_SIZE))
        debug_text = font.render(f"Player Tile: {player_tile}", True, (255, 255, 0))
        screen.blit(debug_text, (10, 35))
        
        debug_indicator = hud_font.render("DEBUG MODE (TAB/F1 to toggle)", True, (255, 255, 0))
        screen.blit(debug_indicator, (10, HEIGHT - 25))

    hp_text = hud_font.render(f"HP: {player.health}", True, (0, 0, 0))
    screen.blit(hp_text, (10, 10))

    if player.health <= 0:
        go_text = hud_font.render("GAME OVER", True, (200, 0, 0))
        text_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(go_text, text_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
