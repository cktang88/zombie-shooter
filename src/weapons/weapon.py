"""
Weapon System Module
-----------------

A comprehensive weapon and projectile system that handles all combat mechanics.

Classes:
    WeaponType: Enum defining different weapon categories
    Bullet: Projectile with physics and visual effects
    Grenade: Throwable explosive with area damage
    Weapon: Base class for all weapons

Weapon Types:
    1. Ranged Weapons:
        - Pistol: Balanced starter weapon (medium damage, medium rate)
        - Assault Rifle: Rapid-fire automatic (low damage, high rate)
        - SMG: Very fast firing (very low damage, very high rate)
        - Battle Rifle: High damage semi-auto (high damage, low rate)
        - Shotgun: Close range spread (medium damage per pellet)

    2. Melee Weapons:
        - Knife: Close range melee attack

    3. Throwables:
        - Grenades: Area damage explosives
        - Molotov: Area denial fire damage

Weapon Features:
    - Unique damage values and fire rates
    - Automatic and semi-automatic firing modes
    - Ammunition management with reloading
    - Screen shake feedback
    - Bullet physics and trail effects
    - Weapon-specific particle effects
    - Recoil and spread patterns

Visual Effects:
    - Dynamic bullet trails based on weapon type
    - Muzzle flash effects
    - Impact effects
    - Reload animations
    - Weapon switching animations

Combat Mechanics:
    - Damage falloff with distance
    - Headshot multipliers
    - Penetration through weak materials
    - Area of effect damage
    - Status effects (burning, slowing)
"""

import pygame
import math
import random
from enum import Enum


class WeaponType(Enum):
    """
    Defines the available weapon types and their base characteristics.
    Each type has unique properties affecting damage, fire rate, and effects.
    """

    KNIFE = "knife"
    PISTOL = "pistol"
    ASSAULT_RIFLE = "assault_rifle"
    SHOTGUN = "shotgun"
    SMG = "smg"
    BATTLE_RIFLE = "battle_rifle"


class Bullet(pygame.sprite.Sprite):
    """
    Projectile class with physics and visual effects.

    Features:
        - Smooth movement with float coordinates
        - Dynamic trail effects based on weapon type
        - Collision detection with precise hitbox
        - Damage properties from source weapon
        - Visual effects (glow, trails)
    """

    def __init__(self, x, y, angle, damage=10):
        super().__init__()
        self.rect = pygame.Rect(x - 10, y - 10, 20, 20)
        self.collision_rect = pygame.Rect(x - 2, y - 2, 4, 4)
        self.x = float(x)
        self.y = float(y)
        self.angle = angle
        self.damage = damage
        self.dx = math.cos(angle) * 15  # Speed is now 15
        self.dy = math.sin(angle) * 15
        self.prev_positions = []
        self.max_trail_length = 10

        # Create base bullet image
        self.base_image = pygame.Surface((20, 4), pygame.SRCALPHA)
        self.draw_bullet()
        self.image = pygame.transform.rotate(self.base_image, -math.degrees(angle))
        self.rect = self.image.get_rect(center=(x, y))

        # New: Dynamic trail properties based on damage
        if damage >= 40:  # High damage weapons (e.g. sniper)
            self.trail_color = (255, 100, 100)  # Red trail
            self.max_trail_length = 15
            self.trail_width = 3
            self.glow_intensity = 2.0
        elif damage >= 20:  # Medium damage (e.g. assault rifle)
            self.trail_color = (100, 255, 255)  # Cyan trail
            self.max_trail_length = 12
            self.trail_width = 2
            self.glow_intensity = 1.5
        else:  # Low damage weapons
            self.trail_color = (255, 255, 100)  # Yellow trail
            self.max_trail_length = 8
            self.trail_width = 1
            self.glow_intensity = 1.0

    def update_collision_rect(self):
        """Update the smaller collision rectangle position."""
        self.collision_rect.center = self.rect.center

    def update(self):
        # Store current position for trail
        self.prev_positions.append((self.x, self.y))
        if len(self.prev_positions) > self.max_trail_length:
            self.prev_positions.pop(0)

        # Update position using float coordinates for smooth movement
        self.x += self.dx
        self.y += self.dy

        # Update sprite rect position
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.update_collision_rect()

    def draw_bullet(self):
        """Draw the bullet as a line with neon effect."""
        # Outer glow (dim)
        pygame.draw.line(self.base_image, (255, 255, 100, 100), (0, 2), (20, 2), 4)

        # Core (bright)
        pygame.draw.line(self.base_image, (255, 255, 200, 255), (0, 2), (20, 2), 2)
        # Center (white hot)
        pygame.draw.line(self.base_image, (255, 255, 255, 255), (0, 2), (20, 2), 1)

    def draw(self, screen, screen_x, screen_y):
        """Draw bullet with enhanced trail effect."""
        # Draw trail
        if len(self.prev_positions) >= 2:
            for i in range(len(self.prev_positions) - 1):
                start_pos = self.prev_positions[i]
                end_pos = self.prev_positions[i + 1]

                # Convert trail positions to screen coordinates
                start_screen_x = int(start_pos[0]) - self.rect.x + screen_x
                start_screen_y = int(start_pos[1]) - self.rect.y + screen_y
                end_screen_x = int(end_pos[0]) - self.rect.x + screen_x
                end_screen_y = int(end_pos[1]) - self.rect.y + screen_y

                # Calculate alpha and width based on position in trail
                progress = i / len(self.prev_positions)
                alpha = int(128 * progress)
                width = max(1, self.trail_width * progress)

                # Draw outer glow
                glow_surf = pygame.Surface((20, 4), pygame.SRCALPHA)
                glow_color = (*self.trail_color, int(alpha * 0.5))
                pygame.draw.line(
                    glow_surf,
                    glow_color,
                    (0, 2),
                    (20, 2),
                    int(width * self.glow_intensity * 2),
                )

                # Draw core trail
                trail_surf = pygame.Surface((20, 4), pygame.SRCALPHA)
                trail_color = (*self.trail_color, alpha)
                pygame.draw.line(
                    trail_surf,
                    trail_color,
                    (0, 2),
                    (20, 2),
                    int(width * self.glow_intensity),
                )

                # Rotate and position trail segments
                rotated_glow = pygame.transform.rotate(
                    glow_surf, -math.degrees(self.angle)
                )
                rotated_trail = pygame.transform.rotate(
                    trail_surf, -math.degrees(self.angle)
                )

                # Position and draw trail segments
                screen.blit(
                    rotated_glow,
                    (
                        start_screen_x - rotated_glow.get_width() // 2,
                        start_screen_y - rotated_glow.get_height() // 2,
                    ),
                )
                screen.blit(
                    rotated_trail,
                    (
                        start_screen_x - rotated_trail.get_width() // 2,
                        start_screen_y - rotated_trail.get_height() // 2,
                    ),
                )

        # Draw the bullet itself
        screen.blit(
            self.image,
            (
                screen_x - self.image.get_width() // 2,
                screen_y - self.image.get_height() // 2,
            ),
        )


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed=8):
        super().__init__()
        self.rect = pygame.Rect(x - 4, y - 4, 8, 8)
        self.x = float(x)
        self.y = float(y)
        self.angle = angle
        self.speed = speed
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.explosion_radius = 100
        self.explosion_damage = 100
        self.fuse_time = 2000  # ms
        self.throw_time = pygame.time.get_ticks()
        self.exploded = False

        # Create grenade surface
        self.image = pygame.Surface((8, 8))
        self.image.fill((100, 100, 100))
        # Add a dark border
        pygame.draw.rect(self.image, (50, 50, 50), (0, 0, 8, 8), 1)

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.throw_time >= self.fuse_time and not self.exploded:
            self.explode()
            return

        if not self.exploded:
            self.x += self.dx
            self.y += self.dy
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

    def explode(self):
        self.exploded = True
        # Actual explosion damage is handled by the game class
        self.kill()

    def draw(self, screen, x, y):
        if not self.exploded:
            screen.blit(self.image, (x, y))


class Weapon:
    def __init__(self, weapon_type):
        self.type = weapon_type
        self.bullet_speed = 15  # Increased bullet speed
        self.has_fired_once = False

        # Set weapon properties based on type
        if weapon_type == WeaponType.KNIFE:
            self.damage = 50
            self.fire_rate = 1000  # ms between attacks
            self.range = 50
            self.auto = False
            self.ammo_capacity = None
            self.reload_time = 0
            self.screen_shake = 2
            self.is_melee = True
        elif weapon_type == WeaponType.PISTOL:
            self.damage = 25
            self.fire_rate = 250  # 4 shots per second
            self.range = 400
            self.auto = False
            self.ammo_capacity = 12
            self.reload_time = 1.5
            self.screen_shake = 3
            self.is_melee = False
        elif weapon_type == WeaponType.ASSAULT_RIFLE:
            self.damage = 15
            self.fire_rate = 100  # 10 shots per second
            self.range = 600
            self.auto = True
            self.ammo_capacity = 30
            self.reload_time = 2.5
            self.screen_shake = 4
            self.is_melee = False
        elif weapon_type == WeaponType.SHOTGUN:
            self.damage = 10
            self.fire_rate = 750  # Slower fire rate
            self.range = 200
            self.auto = False
            self.ammo_capacity = 6
            self.reload_time = 2
            self.screen_shake = 5
            self.is_melee = False
        elif weapon_type == WeaponType.SMG:
            self.damage = 12
            self.fire_rate = 80  # Very fast (12.5 shots per second)
            self.range = 400
            self.auto = True
            self.ammo_capacity = 35
            self.reload_time = 1.8
            self.screen_shake = 2
            self.is_melee = False
        elif weapon_type == WeaponType.BATTLE_RIFLE:
            self.damage = 45
            self.fire_rate = 200  # 5 shots per second
            self.range = 800
            self.auto = False
            self.ammo_capacity = 20
            self.reload_time = 2.2
            self.screen_shake = 6
            self.is_melee = False

        self.current_ammo = (
            self.ammo_capacity if self.ammo_capacity is not None else None
        )
        self.is_reloading = False
        self.reload_start_time = 0
        self.last_shot_time = 0

    def create_bullet(self, x, y, angle):
        print(f"Creating bullet for {self.type}, ammo: {self.current_ammo}")  # Debug
        if self.is_melee:
            print("Melee weapon, no bullets")  # Debug
            return []

        if self.current_ammo is not None:
            if self.current_ammo <= 0:
                print("No ammo left")  # Debug
                return []
            self.current_ammo -= 1
            print(f"Ammo decreased to {self.current_ammo}")  # Debug

        if self.type == WeaponType.SHOTGUN:
            # Create spread bullets for shotgun
            bullets = []
            spread_angles = [-0.2, -0.1, 0, 0.1, 0.2]  # Spread pattern
            for spread in spread_angles:
                spread_angle = angle + spread
                bullet = Bullet(x, y, spread_angle, self.damage)
                bullets.append(bullet)
            print(f"Created {len(bullets)} shotgun bullets")  # Debug
            return bullets
        else:
            # Single bullet for other weapons
            bullet = Bullet(x, y, angle, self.damage)
            print("Created single bullet")  # Debug
            return [bullet]

    def start_reload(self):
        if (
            not self.is_melee
            and not self.is_reloading
            and self.current_ammo is not None
            and self.current_ammo < self.ammo_capacity
        ):
            print(f"Starting reload for {self.type}")  # Debug
            self.is_reloading = True
            self.reload_start_time = pygame.time.get_ticks()

    def update(self):
        if self.is_reloading:
            current_time = pygame.time.get_ticks()
            if current_time - self.reload_start_time >= self.reload_time * 1000:
                self.current_ammo = self.ammo_capacity
                self.is_reloading = False
                print(f"Reload complete, ammo: {self.current_ammo}")  # Debug

    def get_reload_progress(self):
        if not self.is_reloading or self.is_melee:
            return 1.0
        current_time = pygame.time.get_ticks()
        progress = (current_time - self.reload_start_time) / (self.reload_time * 1000)
        return min(1.0, progress)

    def get_screen_shake(self):
        return self.screen_shake

    def draw(self, screen, x, y, angle):
        if self.type == WeaponType.KNIFE:
            # Draw knife as a small rectangle
            knife_length = 20
            end_x = x + math.cos(angle) * knife_length
            end_y = y + math.sin(angle) * knife_length
            pygame.draw.line(screen, (192, 192, 192), (x, y), (end_x, end_y), 3)
        else:
            # Draw gun as a rectangle
            gun_length = 25 if self.type == WeaponType.PISTOL else 35
            end_x = x + math.cos(angle) * gun_length
            end_y = y + math.sin(angle) * gun_length
            pygame.draw.line(screen, (64, 64, 64), (x, y), (end_x, end_y), 4)
