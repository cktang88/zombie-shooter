"""
Player Entity Module
-----------------

The main player character with movement, combat, and inventory systems.

Features:
    1. Movement System:
        - Smooth WASD/Arrow key movement
        - Diagonal movement normalization
        - World boundary collision
        - Movement state tracking for effects
        - Camera following with smoothing

    2. Combat System:
        - Mouse aim and shooting
        - Multiple weapon types
        - Weapon switching
        - Ammo management
        - Grenade throwing
        - Melee combat
        - Health system with damage handling

    3. Inventory System:
        - Multiple weapon slots
        - Grenade inventory
        - Weapon cycling
        - Ammunition tracking
        - Reload management

    4. Visual Effects:
        - Health bar with gradient
        - Ammo counter
        - Reload progress bar
        - Weapon display
        - Movement particles
        - Combat effects
        - Damage feedback

    5. Interaction System:
        - Structure placement
        - Item pickup
        - Shop interaction
        - Resource management

States:
    - Moving/Stationary
    - Firing/Not Firing
    - Reloading
    - Taking Damage
    - Dead/Alive
"""

import pygame
import math
from ..weapons.weapon import Weapon, WeaponType, Grenade


class Player(pygame.sprite.Sprite):
    """
    Player character class handling movement, combat, and visual representation.

    Attributes:
        Movement:
            - position (x, y): Float coordinates for smooth movement
            - speed: Movement velocity
            - is_moving: Current movement state

        Combat:
            - health: Current health points
            - max_health: Maximum health capacity
            - weapons: List of available weapons
            - current_weapon: Active weapon reference
            - is_firing: Current firing state

        Inventory:
            - grenades: Number of available grenades
            - weapon_slots: Available weapon positions
            - current_weapon_index: Active weapon slot
    """

    def __init__(self, x, y, game=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 7
        self.health = 100
        self.angle = 0
        self.game = game

        # Movement state
        self.is_moving = False
        self.x = float(x)
        self.y = float(y)

        # Weapons
        self.weapons = [
            Weapon(WeaponType.PISTOL),
            Weapon(WeaponType.KNIFE),
            Weapon(WeaponType.ASSAULT_RIFLE),
            Weapon(WeaponType.SMG),
            Weapon(WeaponType.SHOTGUN),
            Weapon(WeaponType.BATTLE_RIFLE),
        ]
        # Set game reference for all weapons
        for weapon in self.weapons:
            weapon.set_game(game)

        self.current_weapon_index = 0
        self.current_weapon = self.weapons[self.current_weapon_index]

        # Grenades
        self.grenades = 3
        self.grenade_cooldown = 2000  # ms
        self.last_grenade_time = 0

        # Combat state
        self.is_firing = False
        self.max_health = 100

    def update(self, mouse_world_x, mouse_world_y):
        # Get keyboard input
        keys = pygame.key.get_pressed()

        # Movement
        dx = 0
        dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed

        # Update movement state
        self.is_moving = dx != 0 or dy != 0

        # Apply diagonal movement normalization
        if dx != 0 and dy != 0:
            dx *= 0.7071  # 1/√2
            dy *= 0.7071

        # Update position with world bounds checking
        new_x = self.x + dx
        new_y = self.y + dy

        # Keep player within world bounds
        if self.game:
            new_x = max(0, min(new_x, self.game.world_width - self.rect.width))
            new_y = max(0, min(new_y, self.game.world_height - self.rect.height))

        # Update float positions first
        self.x = new_x
        self.y = new_y

        # Then update rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Calculate angle to mouse in world coordinates
        dx = mouse_world_x - self.rect.centerx
        dy = mouse_world_y - self.rect.centery
        self.angle = math.degrees(math.atan2(dy, dx))

        # Update weapon
        if self.current_weapon:
            self.current_weapon.update()

        # Handle shooting based on weapon type and state
        if self.is_firing and self.current_weapon:
            current_time = pygame.time.get_ticks()
            time_since_last_shot = current_time - self.current_weapon.last_shot_time
            if time_since_last_shot >= self.current_weapon.fire_rate:
                if self.current_weapon.auto or not self.current_weapon.has_fired_once:
                    bullets = self.shoot()
                    if bullets and self.game:
                        self.game.bullets.add(bullets)
                        if not self.current_weapon.auto:
                            self.current_weapon.has_fired_once = True

    def handle_event(self, event):
        """Handle player input events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.current_weapon.is_reloading:
                    # Continue reload if in progress
                    self.current_weapon.continue_reload()
                else:
                    # Start shooting
                    self.is_firing = True
                    bullets = self.shoot()
                    if bullets and self.game:
                        self.game.bullets.add(bullets)
                    return True
            elif event.button == 3:  # Right click
                if self.grenades > 0:
                    self.throw_grenade()
                    return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click released
                self.is_firing = False
                if self.current_weapon:
                    self.current_weapon.has_fired_once = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Reload
                if self.current_weapon and not self.current_weapon.is_reloading:
                    self.current_weapon.start_reload()
            elif event.key == pygame.K_q:
                self.cycle_weapon()

    def cycle_weapon(self):
        if len(self.weapons) > 1:
            self.current_weapon_index = (self.current_weapon_index + 1) % len(
                self.weapons
            )
            self.current_weapon = self.weapons[self.current_weapon_index]
            self.is_firing = False  # Reset firing state when switching weapons

    def shoot(self):
        if not self.current_weapon:
            return []

        current_time = pygame.time.get_ticks()
        time_since_last_shot = current_time - self.current_weapon.last_shot_time

        if time_since_last_shot >= self.current_weapon.fire_rate:
            # Handle melee weapon (knife)
            if self.current_weapon.is_melee:
                # Get mouse position in world coordinates
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if self.game:
                    mouse_x, mouse_y = self.game.screen_to_world(mouse_x, mouse_y)

                # Calculate distance to mouse
                dx = mouse_x - self.rect.centerx
                dy = mouse_y - self.rect.centery
                distance = math.sqrt(dx * dx + dy * dy)

                # Only hit if within range
                if distance <= self.current_weapon.range:
                    # Find zombies in range
                    if self.game:
                        for zombie in self.game.zombies:
                            zombie_dx = zombie.rect.centerx - self.rect.centerx
                            zombie_dy = zombie.rect.centery - self.rect.centery
                            zombie_dist = math.sqrt(
                                zombie_dx * zombie_dx + zombie_dy * zombie_dy
                            )

                            if zombie_dist <= self.current_weapon.range:
                                zombie.take_damage(self.current_weapon.damage)

                        # Add screen shake for successful hit
                        self.game.add_screen_shake(0.5)  # Less shake for melee
                    self.current_weapon.last_shot_time = current_time
                return []
            else:
                # Handle regular weapons
                bullets = self.current_weapon.create_bullet(
                    self.rect.centerx, self.rect.centery, math.radians(self.angle)
                )

                if bullets:
                    # Add screen shake when shooting
                    if self.game:
                        # Different shake intensities for different weapons
                        shake_intensity = {
                            WeaponType.PISTOL: 0.7,
                            WeaponType.ASSAULT_RIFLE: 0.5,
                            WeaponType.SMG: 0.3,
                            WeaponType.SHOTGUN: 1.2,
                            WeaponType.BATTLE_RIFLE: 0.9,
                        }.get(self.current_weapon.type, 0.5)
                        self.game.add_screen_shake(shake_intensity)
                    self.current_weapon.last_shot_time = current_time
                    return bullets

        return []

    def throw_grenade(self):
        """Throw a grenade in the direction the player is facing."""
        current_time = pygame.time.get_ticks()
        if (
            self.grenades > 0
            and current_time - self.last_grenade_time > self.grenade_cooldown
            and self.game
        ):
            # Calculate throw direction based on mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_x, world_y = self.game.screen_to_world(mouse_x, mouse_y)

            # Calculate direction vector
            dx = world_x - self.rect.centerx
            dy = world_y - self.rect.centery
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx = dx / length
                dy = dy / length

            # Create and add grenade
            grenade = Grenade(
                self.rect.centerx, self.rect.centery, dx, dy  # Normalized direction
            )
            self.game.grenades.add(grenade)

            # Update state
            self.grenades -= 1
            self.last_grenade_time = current_time
            print(f"Threw grenade, {self.grenades} remaining")  # Debug

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.kill()

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def draw(self, screen, x, y):
        # Draw player body
        pygame.draw.circle(
            screen,
            (100, 100, 255),
            (x + self.rect.width // 2, y + self.rect.height // 2),
            20,
        )

        # Draw health bar above player
        bar_width = 40
        bar_height = 4
        bar_x = x + self.rect.width // 2 - bar_width // 2
        bar_y = y - 15

        # Health bar background
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        # Health bar fill
        health_width = int(bar_width * (self.health / self.max_health))
        if health_width > 0:
            pygame.draw.rect(
                screen, (255, 0, 0), (bar_x, bar_y, health_width, bar_height)
            )

        # Draw ammo bar above health bar if weapon uses ammo
        if self.current_weapon and not self.current_weapon.is_melee:
            ammo_y = bar_y - 6
            # Ammo bar background
            pygame.draw.rect(
                screen, (60, 60, 60), (bar_x, ammo_y, bar_width, bar_height)
            )
            # Ammo bar fill
            if (
                self.current_weapon.ammo_capacity is not None
                and self.current_weapon.ammo_capacity > 0
            ):
                ammo_width = int(
                    bar_width
                    * (
                        self.current_weapon.current_ammo
                        / self.current_weapon.ammo_capacity
                    )
                )
                if ammo_width > 0:
                    pygame.draw.rect(
                        screen, (255, 255, 0), (bar_x, ammo_y, ammo_width, bar_height)
                    )

        # Draw reload progress bar if reloading
        if self.current_weapon and self.current_weapon.is_reloading:
            reload_y = bar_y - 12  # Above ammo bar
            # Reload bar background
            pygame.draw.rect(
                screen, (60, 60, 60), (bar_x, reload_y, bar_width, bar_height)
            )
            # Reload bar fill
            reload_progress = self.current_weapon.get_reload_progress()
            reload_width = int(bar_width * reload_progress)
            if reload_width > 0:
                pygame.draw.rect(
                    screen, (0, 255, 255), (bar_x, reload_y, reload_width, bar_height)
                )

        # Draw current weapon
        if self.current_weapon:
            self.current_weapon.draw(
                screen,
                x + self.rect.width // 2,
                y + self.rect.height // 2,
                math.radians(self.angle),
            )
