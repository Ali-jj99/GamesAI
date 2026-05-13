# This file implements the base enemy class with FSM states for Section 1.5 of the coursework

import pygame
import math
from typing import Tuple, List, Optional

from ai.pathfinding import a_star

GridPos = Tuple[int, int]

# I defined these FSM states to meet the coursework requirement of 5 distinct states for Section 1.5
STATE_PATROL = "PATROL"
STATE_CHASE = "CHASE"
STATE_ATTACK = "ATTACK"
STATE_RETREAT = "RETREAT"
STATE_HEAL = "HEAL"


class EnemyBase:
    _id_counter = 1

    def __init__(self, x: int, y: int, color=(200, 0, 0), size=12, speed=2.0):
        self.x = x
        self.y = y
        self.size = size
        self.base_color = color
        self.color = color
        self.speed = speed

        self.health = 50
        self.id = EnemyBase._id_counter
        EnemyBase._id_counter += 1

        # I added this timer so enemies flash white when they take damage
        self.hit_timer = 0

        self.attack_cooldown = 0
        
        # I added cooldowns so enemies don't shoot or melee attack too frequently
        self.shoot_cooldown = 0
        self.SHOOT_COOLDOWN_MAX = 90
        self.SHOOT_COOLDOWN_ATTACK = 60

        self.state = STATE_PATROL
        
        # I made these constants so subclasses can customize enemy behavior
        self.DETECTION_RADIUS = 150
        self.ATTACK_RANGE = 60
        self.ATTACK_RADIUS = 20
        self.LOW_HP_THRESHOLD = 15
        self.HEALED_THRESHOLD = 35
        self.SAFE_DISTANCE = 200
        self.LOST_SIGHT_RADIUS = 250
        self.MAX_HEALTH = 50
        self.RETREAT_HEALTH_THRESHOLD = self.LOW_HP_THRESHOLD
        
        # I track recent damage so enemies retreat after being hit
        self.recently_hit_timer = 0
        self.RECENTLY_HIT_DURATION = 180
        
        self.heal_timer = 0
        self.HEAL_RATE = 1
        
        self.patrol_target = None
        self.patrol_timer = 0
        self.patrol_waypoints = []
        self.current_waypoint_index = 0
        
        self.lost_sight_timer = 0
        self.LOST_SIGHT_DURATION = 180
        
        self.retreat_target = None
        self.retreat_timer = 0
        
        # I added bravery_factor to create probabilistic behavior for the coursework
        self.bravery_factor = 0.3

    def pixel_to_tile(self, tile_size: int) -> GridPos:
        # I convert pixel coordinates to grid tile coordinates for pathfinding
        row = int((self.y + self.size / 2) / tile_size)
        col = int((self.x + self.size / 2) / tile_size)
        return row, col

    def take_damage(self, amount: int):
        # I reduce health and trigger visual feedback when enemies are hit
        self.health -= amount
        self.hit_timer = 5
        self.recently_hit_timer = self.RECENTLY_HIT_DURATION
        
        # I added probabilistic retreat logic so heavy hits make enemies more likely to retreat
        import random
        if self.state == STATE_CHASE or self.state == STATE_ATTACK:
            heavy_hit = amount >= 25
            base_chance = 0.6
            if self.state == STATE_ATTACK and heavy_hit:
                base_chance = 0.8
            effective_chance = max(0.1, base_chance - self.bravery_factor * 0.2)
            if heavy_hit or random.random() < effective_chance or self.health <= self.LOW_HP_THRESHOLD:
                self.state = STATE_RETREAT

    def _get_path(self, arena, start_tile: GridPos, goal_tile: GridPos) -> Optional[List[GridPos]]:
        # I use A* as the default pathfinding, but subclasses can override this
        return a_star(arena, start_tile, goal_tile)

    def _distance_to_player(self, player_pos_px: Tuple[float, float]) -> float:
        # I calculate the distance to the player so enemies know when to chase or retreat
        px, py = player_pos_px
        dx = (self.x + self.size / 2) - px
        dy = (self.y + self.size / 2) - py
        return math.sqrt(dx * dx + dy * dy)

    def _has_line_of_sight(self, arena, player_pos_px: Tuple[float, float], tile_size: int) -> bool:
        # I check if there are walls or obstacles blocking the enemy's view of the player
        from world.arena_generator import WALL, OBSTACLE
        
        enemy_tile = self.pixel_to_tile(tile_size)
        player_tile = (
            int(player_pos_px[1] / tile_size),
            int(player_pos_px[0] / tile_size),
        )
        
        r0, c0 = enemy_tile
        r1, c1 = player_tile
        
        dr = abs(r1 - r0)
        dc = abs(c1 - c0)
        steps = max(dr, dc)
        
        if steps == 0:
            return True
        
        for i in range(1, steps):
            r = int(r0 + (r1 - r0) * i / steps)
            c = int(c0 + (c1 - c0) * i / steps)
            
            rows, cols = arena.shape
            if 0 <= r < rows and 0 <= c < cols:
                tile_id = arena[r, c]
                if tile_id in [WALL, OBSTACLE]:
                    return False
        
        return True

    def _update_state(self, arena, player_pos_px: Tuple[float, float], tile_size: int):
        # This part implements the FSM state transitions
        import random
        distance = self._distance_to_player(player_pos_px)
        
        if self.recently_hit_timer > 0:
            self.recently_hit_timer -= 1
        
        # I check RETREAT first because it has the highest priority
        should_retreat = False
        if self.health <= self.LOW_HP_THRESHOLD:
            should_retreat = True
        elif self.recently_hit_timer > 0:
            # I use bravery_factor to create probabilistic behavior when enemies are hit
            if (self.state == STATE_CHASE or self.state == STATE_ATTACK) and random.random() < self.bravery_factor:
                pass
            else:
                should_retreat = True
        
        if should_retreat and self.state != STATE_RETREAT:
            self.state = STATE_RETREAT
            self.retreat_target = None
            return
        
        # I check ATTACK state before CHASE so enemies enter close combat when player is very close
        if self.state == STATE_ATTACK and distance > self.ATTACK_RANGE:
            if distance <= self.DETECTION_RADIUS:
                has_los = self._has_line_of_sight(arena, player_pos_px, tile_size)
                if has_los:
                    self.state = STATE_CHASE
                    self.lost_sight_timer = 0
                else:
                    self.state = STATE_PATROL
                    self.lost_sight_timer = 0
            else:
                self.state = STATE_PATROL
                self.lost_sight_timer = 0
            return

        if distance <= self.ATTACK_RANGE:
            has_los = self._has_line_of_sight(arena, player_pos_px, tile_size)
            
            if has_los:
                if self.health > self.LOW_HP_THRESHOLD:
                    if self.state == STATE_CHASE:
                        self.state = STATE_ATTACK
                        self.lost_sight_timer = 0
                    elif self.state == STATE_ATTACK:
                        self.lost_sight_timer = 0
                    elif self.state == STATE_PATROL or self.state == STATE_HEAL:
                        self.state = STATE_ATTACK
                        self.lost_sight_timer = 0
            return
        
        # I check CHASE state when player is detected but outside attack range
        if distance <= self.DETECTION_RADIUS:
            has_los = self._has_line_of_sight(arena, player_pos_px, tile_size)
            
            if has_los:
                if self.state == STATE_PATROL:
                    self.state = STATE_CHASE
                    self.lost_sight_timer = 0
                elif self.state == STATE_HEAL:
                    self.state = STATE_CHASE
                    self.lost_sight_timer = 0
                elif self.state == STATE_CHASE:
                    self.lost_sight_timer = 0
                elif self.state == STATE_ATTACK:
                    self.state = STATE_CHASE
                    self.lost_sight_timer = 0
                elif self.state == STATE_RETREAT:
                    pass
            else:
                if self.state == STATE_CHASE or self.state == STATE_ATTACK:
                    self.lost_sight_timer += 1
                    if self.lost_sight_timer > self.LOST_SIGHT_DURATION:
                        self.state = STATE_PATROL
                        self.lost_sight_timer = 0
            return
        
        # I check HEAL state when enemy is safe and needs to recover health
        if distance > self.SAFE_DISTANCE and self.recently_hit_timer == 0:
            if self.health < self.HEALED_THRESHOLD:
                if self.state == STATE_RETREAT:
                    self.state = STATE_HEAL
                    self.heal_timer = 0
                elif self.state == STATE_HEAL:
                    pass
                else:
                    if self.state != STATE_CHASE and self.state != STATE_ATTACK:
                        self.state = STATE_HEAL
                        self.heal_timer = 0
            elif self.state == STATE_HEAL and self.health >= self.HEALED_THRESHOLD:
                if distance > self.DETECTION_RADIUS:
                    self.state = STATE_PATROL
            return
        
        # I set PATROL as the default state when player is too far away
        if distance > self.DETECTION_RADIUS:
            if self.state == STATE_CHASE or self.state == STATE_ATTACK:
                self.state = STATE_PATROL
                self.lost_sight_timer = 0
            elif self.state == STATE_RETREAT:
                if self.health < self.HEALED_THRESHOLD:
                    self.state = STATE_HEAL
                else:
                    self.state = STATE_PATROL
            elif self.state == STATE_HEAL and self.health >= self.HEALED_THRESHOLD:
                self.state = STATE_PATROL

    def _get_patrol_target(self, arena, tile_size: int) -> Optional[GridPos]:
        # I generate a random nearby walkable tile for enemies to patrol to
        import random
        rows, cols = arena.shape
        current_tile = self.pixel_to_tile(tile_size)
        
        if self.patrol_waypoints:
            if self.current_waypoint_index >= len(self.patrol_waypoints):
                self.current_waypoint_index = 0
            target = self.patrol_waypoints[self.current_waypoint_index]
            
            if abs(current_tile[0] - target[0]) <= 1 and abs(current_tile[1] - target[1]) <= 1:
                self.current_waypoint_index = (self.current_waypoint_index + 1) % len(self.patrol_waypoints)
                target = self.patrol_waypoints[self.current_waypoint_index]
            
            return target
        
        for _ in range(10):
            offset_r = random.randint(-5, 5)
            offset_c = random.randint(-5, 5)
            target_r = current_tile[0] + offset_r
            target_c = current_tile[1] + offset_c
            
            if 0 <= target_r < rows and 0 <= target_c < cols:
                tile_id = arena[target_r, target_c]
                if tile_id in [0, 3, 4]:
                    return (target_r, target_c)
        
        return current_tile
    
    def _get_retreat_target(self, arena, player_pos_px: Tuple[float, float], tile_size: int) -> Optional[GridPos]:
        # I find a tile far from the player so enemies can retreat safely
        rows, cols = arena.shape
        enemy_tile = self.pixel_to_tile(tile_size)
        player_tile = (
            int(player_pos_px[1] / tile_size),
            int(player_pos_px[0] / tile_size),
        )
        
        best_target = None
        best_distance = 0
        
        import random
        for _ in range(20):
            offset_r = random.randint(-8, 8)
            offset_c = random.randint(-8, 8)
            target_r = enemy_tile[0] + offset_r
            target_c = enemy_tile[1] + offset_c
            
            if 0 <= target_r < rows and 0 <= target_c < cols:
                tile_id = arena[target_r, target_c]
                if tile_id in [0, 3, 4]:
                    dist_from_player = abs(target_r - player_tile[0]) + abs(target_c - player_tile[1])
                    if dist_from_player > best_distance:
                        best_distance = dist_from_player
                        best_target = (target_r, target_c)
        
        return best_target or enemy_tile

    def _get_terrain_speed_multiplier(self, arena, tile_size: int) -> float:
        # I slow down enemies on MUD and RAIN tiles just like the player
        current_tile = self.pixel_to_tile(tile_size)
        r, c = current_tile
        rows, cols = arena.shape
        
        if 0 <= r < rows and 0 <= c < cols:
            tile_id = arena[r, c]
            if tile_id == 3:
                return 0.5
            elif tile_id == 4:
                return 0.7
        return 1.0

    def _move_towards_target(self, arena, target_tile: GridPos, tile_size: int, occupied_tiles: Optional[set] = None):
        # I use pathfinding to move enemies toward their target while avoiding other NPCs
        if occupied_tiles is None:
            occupied_tiles = set()
        
        start_tile = self.pixel_to_tile(tile_size)
        path = self._get_path(arena, start_tile, target_tile)
        
        if not path or len(path) < 2:
            return
        
        next_tile = path[1]
        
        # I prevent enemies from moving into tiles occupied by other enemies
        if next_tile in occupied_tiles:
            return
        
        target_cx = next_tile[1] * tile_size + tile_size / 2
        target_cy = next_tile[0] * tile_size + tile_size / 2

        dx = target_cx - (self.x + self.size / 2)
        dy = target_cy - (self.y + self.size / 2)
        dist = (dx * dx + dy * dy) ** 0.5 or 1.0

        # I apply terrain speed multipliers so enemies slow down on mud and rain
        speed_mult = self._get_terrain_speed_multiplier(arena, tile_size)
        effective_speed = self.speed * speed_mult

        step_x = (dx / dist) * effective_speed
        step_y = (dy / dist) * effective_speed

        self.x += step_x
        self.y += step_y

    def update(self, arena, player_pos_px: Tuple[float, float], tile_size: int, occupied_tiles: Optional[set] = None):
        # This part updates the enemy's FSM state and makes it behave according to its current state
        rows, cols = arena.shape
        player_x, player_y = player_pos_px

        if self.hit_timer > 0:
            self.hit_timer -= 1
        self.color = (255, 255, 255) if self.hit_timer > 0 else self.base_color

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self._update_state(arena, player_pos_px, tile_size)

        # I implement different behaviors for each FSM state
        if self.state == STATE_PATROL:
            self.patrol_timer += 1
            if self.patrol_timer > 120 or self.patrol_target is None:
                self.patrol_target = self._get_patrol_target(arena, tile_size)
                self.patrol_timer = 0
            
            if self.patrol_target:
                self._move_towards_target(arena, self.patrol_target, tile_size, occupied_tiles)
                
        elif self.state == STATE_CHASE:
            # I make enemies pathfind directly to the player when chasing
            goal_tile = (
                int(player_y / tile_size),
                int(player_x / tile_size),
            )
            goal_r = max(0, min(rows - 1, goal_tile[0]))
            goal_c = max(0, min(cols - 1, goal_tile[1]))
            goal_tile = (goal_r, goal_c)
            self._move_towards_target(arena, goal_tile, tile_size, occupied_tiles)
            
        elif self.state == STATE_ATTACK:
            # I make enemies move very slowly in ATTACK state so they focus on shooting
            distance = self._distance_to_player(player_pos_px)
            
            if distance > self.ATTACK_RANGE * 0.8:
                goal_tile = (
                    int(player_y / tile_size),
                    int(player_x / tile_size),
                )
                goal_r = max(0, min(rows - 1, goal_tile[0]))
                goal_c = max(0, min(cols - 1, goal_tile[1]))
                goal_tile = (goal_r, goal_c)
                old_speed = self.speed
                self.speed = old_speed * 0.3
                self._move_towards_target(arena, goal_tile, tile_size, occupied_tiles)
                self.speed = old_speed
            
        elif self.state == STATE_RETREAT:
            # I make enemies pathfind away from the player when retreating
            if self.retreat_target is None:
                self.retreat_target = self._get_retreat_target(arena, player_pos_px, tile_size)
                self.retreat_timer = 0
            
            current_tile = self.pixel_to_tile(tile_size)
            if self.retreat_target:
                dist_to_target = abs(current_tile[0] - self.retreat_target[0]) + abs(current_tile[1] - self.retreat_target[1])
                if dist_to_target <= 2:
                    self.retreat_target = self._get_retreat_target(arena, player_pos_px, tile_size)
            
            if self.retreat_target:
                self._move_towards_target(arena, self.retreat_target, tile_size, occupied_tiles)
            
            self.retreat_timer += 1
            
        elif self.state == STATE_HEAL:
            # I make enemies regenerate health slowly while in HEAL state
            self.heal_timer += 1
            if self.heal_timer >= 2:
                self.health = min(self.MAX_HEALTH, self.health + 1)
                self.heal_timer = 0
            
            if self.patrol_timer % 60 == 0:
                current_tile = self.pixel_to_tile(tile_size)
                import random
                offset_r = random.randint(-1, 1)
                offset_c = random.randint(-1, 1)
                target_r = current_tile[0] + offset_r
                target_c = current_tile[1] + offset_c
                rows, cols = arena.shape
                if 0 <= target_r < rows and 0 <= target_c < cols:
                    tile_id = arena[target_r, target_c]
                    if tile_id in [0, 3, 4]:
                        self.patrol_target = (target_r, target_c)
            
            if self.patrol_target:
                self._move_towards_target(arena, self.patrol_target, tile_size, occupied_tiles)
            
            self.patrol_timer += 1

    def shoot_at_player(self, player_pos_px: Tuple[float, float]) -> Optional['Projectile']:
        # I allow enemies to shoot projectiles at the player when in CHASE or ATTACK state
        if self.shoot_cooldown > 0:
            return None
        
        if self.state != STATE_CHASE and self.state != STATE_ATTACK:
            return None
        
        from entities.projectile import Projectile
        
        enemy_cx = self.x + self.size / 2
        enemy_cy = self.y + self.size / 2
        
        player_x, player_y = player_pos_px
        
        # I store owner_type in the projectile so the damage model knows which enemy type fired it
        projectile = Projectile(
            enemy_cx,
            enemy_cy,
            player_x,
            player_y,
            speed=6,
            radius=3,
            color=(255, 255, 0),
            owner_type=self.__class__.__name__,
        )
        
        # I use shorter cooldown in ATTACK state so enemies shoot more aggressively
        if self.state == STATE_ATTACK:
            self.shoot_cooldown = self.SHOOT_COOLDOWN_ATTACK
        else:
            self.shoot_cooldown = self.SHOOT_COOLDOWN_MAX
        
        return projectile

    def draw(self, screen, font: pygame.font.Font):
        # I draw the enemy as a colored square with a label showing ID, health, and FSM state
        rect = pygame.Rect(self.x, self.y, self.size, self.size)
        pygame.draw.rect(screen, self.color, rect)

        label = f"E{self.id} ({self.health}) [{self.state}]"
        text_surf = font.render(label, True, (0, 0, 0))
        screen.blit(text_surf, (self.x, self.y - 14))
