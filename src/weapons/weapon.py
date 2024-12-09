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

    def __init__(self, x, y, angle, damage=10, bullet_speed=15, game=None):
        """Initialize a bullet with position, angle, damage, and speed.

        Args:
            x (float): X position
            y (float): Y position
            angle (float): Direction angle in radians
            damage (int, optional): Bullet damage. Defaults to 10.
            bullet_speed (float, optional): Bullet velocity. Defaults to 15.
            game (Game, optional): Reference to game instance. Defaults to None.
        """
        super().__init__()
        self.game = game
        self.size = self.get_size_from_damage(damage)
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)  # Ensure angle is float
        self.damage = damage
        self.dx = math.cos(self.angle) * bullet_speed
        self.dy = math.sin(self.angle) * bullet_speed

        # Colors
        self.bullet_color = self.get_color_from_damage(damage)
        self.trail_color = self.get_trail_color_from_damage(damage)

        # Create collision rect
        self.rect = pygame.Rect(x - 2, y - 2, 4, 4)
        self.collision_rect = pygame.Rect(x - 2, y - 2, 4, 4)

        # Create bullet surface
        self.length = 20  # Length of the bullet line
        self.base_image = pygame.Surface(
            (self.length + 4, self.size * 4), pygame.SRCALPHA
        )
        self.draw_bullet()
        self.image = pygame.transform.rotate(self.base_image, -math.degrees(self.angle))
        self.rect = self.image.get_rect(center=(x, y))

    def get_size_from_damage(self, damage):
        """Return bullet size based on damage."""
        if damage >= 40:  # High damage (e.g., sniper)
            return 2
        elif damage >= 20:  # Medium damage
            return 1.5
        else:  # Low damage
            return 1

    def get_color_from_damage(self, damage):
        """Return bullet color based on damage."""
        if damage >= 40:  # High damage weapons (e.g. sniper)
            return (255, 255, 200)  # Bright yellow-white
        elif damage >= 20:  # Medium damage (e.g. assault rifle)
            return (255, 255, 255)  # Pure white
        else:  # Low damage weapons
            return (255, 255, 150)  # Light yellow

    def get_trail_color_from_damage(self, damage):
        """Return trail color based on damage."""
        if damage >= 40:  # High damage weapons
            return (255, 255, 100)  # Yellow trail
        elif damage >= 20:  # Medium damage
            return (255, 255, 200)  # Light yellow trail
        else:  # Low damage weapons
            return (255, 255, 150)  # Pale yellow trail

    def update_collision_rect(self):
        """Update the smaller collision rectangle position."""
        self.collision_rect.center = self.rect.center

    def update(self):
        """Update bullet position and trail."""
        # Add trail effect if game reference exists
        if self.game and hasattr(self.game, "particle_system"):
            self.game.particle_system.create_bullet_trail(
                self.x, self.y, self.angle, self.trail_color
            )

        # Update position
        self.x += self.dx
        self.y += self.dy

        # Update rectangles
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.collision_rect.center = self.rect.center

        # Update bullet rotation
        self.image = pygame.transform.rotate(self.base_image, -math.degrees(self.angle))

    def draw_bullet(self):
        """Draw the bullet as a line with glow effect."""
        # Calculate line length based on bullet speed
        line_length = 10  # Fixed shorter length for consistency

        # Draw outer glow (wider line)
        pygame.draw.line(
            self.base_image,
            (*self.bullet_color, 100),  # Semi-transparent
            (0, self.size),
            (line_length, self.size),
            max(1, int(self.size * 1.5)),  # Thinner glow
        )

        # Draw core (thinner line)
        pygame.draw.line(
            self.base_image,
            (*self.bullet_color, 255),  # Solid core
            (0, self.size),
            (line_length, self.size),
            max(1, int(self.size)),  # Ensure at least 1px thick
        )

    def draw(self, screen, screen_x, screen_y):
        """Draw bullet with glow effect."""
        # Draw the bullet itself
        screen.blit(
            self.image,
            (
                screen_x - self.image.get_width() // 2,
                screen_y - self.image.get_height() // 2,
            ),
        )


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.rect = pygame.Rect(x - 4, y - 4, 8, 8)
        self.x = float(x)
        self.y = float(y)
        self.dx = dx
        self.dy = dy
        self.speed = 8
        self.explosion_radius = 100
        self.damage = 100
        self.exploded = False
        self.explosion_time = None
        self.explosion_duration = 500  # ms
        self.throw_time = pygame.time.get_ticks()
        self.fuse_time = 2000  # ms

    def update(self, current_time=None):
        """Update grenade position and check for explosion."""
        if current_time is None:
            current_time = pygame.time.get_ticks()

        if not self.exploded:
            # Move grenade
            self.x += self.dx * self.speed
            self.y += self.dy * self.speed
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

            # Check if fuse time is up
            if current_time - self.throw_time >= self.fuse_time:
                self.explode(current_time)
        elif current_time - self.explosion_time > self.explosion_duration:
            self.kill()

    def explode(self, current_time=None):
        """Trigger the grenade explosion."""
        if current_time is None:
            current_time = pygame.time.get_ticks()
        self.exploded = True
        self.explosion_time = current_time

    def draw(self, screen, x, y):
        """Draw the grenade and explosion effects."""
        if not self.exploded:
            # Draw grenade
            pygame.draw.circle(screen, (100, 100, 100), (x + 4, y + 4), 4)
        else:
            # Draw explosion effect
            current_time = pygame.time.get_ticks()
            progress = (current_time - self.explosion_time) / self.explosion_duration
            alpha = int(255 * (1 - progress))
            if alpha > 0:
                # Create explosion surface with transparency
                explosion_surf = pygame.Surface(
                    (self.explosion_radius * 2, self.explosion_radius * 2),
                    pygame.SRCALPHA,
                )

                # Draw multiple circles for explosion effect
                for radius in range(self.explosion_radius, 0, -10):
                    color_factor = radius / self.explosion_radius
                    color = (
                        int(255 * color_factor),  # R
                        int(165 * color_factor),  # G
                        int(0),  # B
                        int(alpha * color_factor),  # A
                    )
                    pygame.draw.circle(
                        explosion_surf,
                        color,
                        (self.explosion_radius, self.explosion_radius),
                        radius,
                    )

                # Draw the explosion
                screen.blit(
                    explosion_surf,
                    (x - self.explosion_radius, y - self.explosion_radius),
                )


class Weapon:
    def __init__(self, weapon_type):
        self.type = weapon_type
        self.is_melee = weapon_type == WeaponType.KNIFE
        self.last_shot_time = 0
        self.is_reloading = False
        self.reload_start_time = 0
        self.reload_stage = 0  # For multi-stage reloads
        self.has_fired_once = False  # Track if weapon has been fired
        self.game = None  # Will be set when weapon is equipped

        # Weapon-specific properties
        if self.type == WeaponType.PISTOL:
            self.damage = 10
            self.fire_rate = 0.7  # seconds between shots
            self.reload_time = 1.2  # seconds
            self.ammo_capacity = 12
            self.bullet_speed = 12
            self.reload_stages = 1
            self.auto = False  # Semi-auto
            self.range = 250  # Medium range (was 500)
        elif self.type == WeaponType.SHOTGUN:
            self.damage = 16  # per pellet
            self.fire_rate = 1.5
            self.reload_time = 0.6  # per shell
            self.ammo_capacity = 6
            self.bullet_speed = 10
            self.reload_stages = 6  # Load shells one by one
            self.auto = False  # Pump action
            self.range = 50  # Short range (was 300)
        elif self.type == WeaponType.SMG:
            self.damage = 10
            self.fire_rate = 0.6
            self.reload_time = 1.8
            self.ammo_capacity = 30
            self.bullet_speed = 14
            self.reload_stages = 1
            self.auto = True  # Full auto
            self.range = 100  # Medium range (was 400)
        elif self.type == WeaponType.ASSAULT_RIFLE:
            self.damage = 20
            self.fire_rate = 0.9
            self.reload_time = 2.2
            self.ammo_capacity = 25
            self.bullet_speed = 25
            self.reload_stages = 2  # Magazine out, magazine in
            self.auto = True  # Full auto
            self.range = 200  # Long range (was 600)
        elif self.type == WeaponType.BATTLE_RIFLE:
            self.damage = 40
            self.fire_rate = 1.5
            self.reload_time = 2.5
            self.ammo_capacity = 10
            self.bullet_speed = 35
            self.reload_stages = 2
            self.auto = False  # Semi-auto
            self.range = 400  # Very long range (was 800)
        else:  # Knife
            self.damage = 50
            self.fire_rate = 0.5
            self.reload_time = 0
            self.ammo_capacity = None
            self.bullet_speed = 0
            self.reload_stages = 0
            self.auto = False  # Manual swing
            self.range = 25  # Very short melee range (was 50)

        self.current_ammo = self.ammo_capacity

    def create_bullet(self, x, y, angle):
        """Create bullet(s) and mark weapon as fired."""
        if self.is_melee:
            print("Melee weapon, no bullets")  # Debug
            return []

        if self.current_ammo is not None:
            if self.current_ammo <= 0:
                return []
            self.current_ammo -= 1
            self.has_fired_once = True  # Mark as fired when bullet is created

        # Get base spread for weapon type
        if self.type == WeaponType.PISTOL:
            base_spread = 0.05  # Small spread
        elif self.type == WeaponType.SHOTGUN:
            base_spread = 0.2  # Wide spread for pellets
        elif self.type == WeaponType.SMG:
            base_spread = 0.15  # Large spread due to rapid fire
        elif self.type == WeaponType.ASSAULT_RIFLE:
            base_spread = 0.08  # Moderate spread
        elif self.type == WeaponType.BATTLE_RIFLE:
            base_spread = 0.03  # Minimal spread, accurate
        else:
            base_spread = 0

        if self.type == WeaponType.SHOTGUN:
            # Create clustered spread for shotgun
            bullets = []
            num_pellets = 6
            # Create a random central deviation
            center_deviation = random.uniform(-base_spread / 2, base_spread / 2)

            for _ in range(num_pellets):
                # Each pellet deviates from the center point
                pellet_spread = random.gauss(center_deviation, base_spread / 3)
                # Clamp spread to reasonable bounds
                pellet_spread = max(-base_spread, min(base_spread, pellet_spread))
                spread_angle = angle + pellet_spread

                bullet = Bullet(
                    x, y, spread_angle, self.damage, self.bullet_speed, self.game
                )
                bullets.append(bullet)
            return bullets
        else:
            # Single bullet with random spread
            spread = random.uniform(-base_spread, base_spread)
            # Add recoil if automatic weapon is firing continuously
            if self.auto and self.has_fired_once:
                spread *= 1.5  # Increase spread for sustained fire

            spread_angle = angle + spread
            bullet = Bullet(
                x, y, spread_angle, self.damage, self.bullet_speed, self.game
            )
            return [bullet]

    def start_reload(self):
        """Start or continue the reload process if conditions are met."""
        if (
            not self.is_melee
            and not self.is_reloading
            and self.current_ammo is not None
            and self.current_ammo < self.ammo_capacity
        ):
            self.is_reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            self.reload_stage = 0
            if self.type in [WeaponType.ASSAULT_RIFLE, WeaponType.BATTLE_RIFLE]:
                # These weapons empty the magazine first
                self.current_ammo = 0

    def continue_reload(self):
        """Continue to the next reload stage when player clicks."""
        if self.is_reloading:
            current_time = pygame.time.get_ticks()
            stage_duration = self.reload_time * 1000  # Time for current stage

            # Check if enough time has passed for current stage
            if current_time - self.reload_start_time >= stage_duration:
                # Handle stage completion
                if self.type == WeaponType.SHOTGUN:
                    # Add one shell
                    if self.current_ammo < self.ammo_capacity:
                        self.current_ammo += 1
                        # Start next stage if not full
                        if self.current_ammo < self.ammo_capacity:
                            self.reload_start_time = current_time
                            self.reload_stage += 1
                        else:
                            self.finish_reload()
                else:
                    # For magazine-based weapons
                    self.reload_stage += 1
                    if self.reload_stage >= self.reload_stages:
                        self.finish_reload()
                    else:
                        self.reload_start_time = current_time

    def update(self):
        """Update weapon state."""
        if self.is_reloading:
            current_time = pygame.time.get_ticks()
            stage_duration = self.reload_time * 1000

            # Auto-cancel reload if taking too long
            if (
                current_time - self.reload_start_time > stage_duration * 3
            ):  # 3x normal duration
                self.is_reloading = False
                self.reload_stage = 0

    def get_reload_progress(self):
        """Get the current reload stage progress as a float between 0 and 1."""
        if not self.is_reloading:
            return 1.0
        current_time = pygame.time.get_ticks()
        stage_duration = self.reload_time * 1000
        progress = (current_time - self.reload_start_time) / stage_duration
        return min(1.0, progress)

    def finish_reload(self):
        """Complete the reload process."""
        self.is_reloading = False
        if self.type != WeaponType.SHOTGUN:  # Shotgun loads shells incrementally
            self.current_ammo = self.ammo_capacity
        self.reload_stage = 0

    def can_shoot(self):
        """Check if the weapon can shoot based on fire rate and ammo."""
        if self.is_reloading:
            return False

        current_time = pygame.time.get_ticks()
        time_since_last_shot = (current_time - self.last_shot_time) / 1000.0

        if time_since_last_shot < self.fire_rate:
            return False

        if self.current_ammo is not None and self.current_ammo <= 0:
            return False

        return True

    def get_screen_shake(self):
        """Get screen shake intensity based on weapon type."""
        shake_values = {
            WeaponType.PISTOL: 0.7,
            WeaponType.SHOTGUN: 1.2,
            WeaponType.SMG: 0.3,
            WeaponType.ASSAULT_RIFLE: 0.5,
            WeaponType.BATTLE_RIFLE: 0.9,
            WeaponType.KNIFE: 0.2,
        }
        return shake_values.get(self.type, 0.5)

    def draw(self, screen, x, y, angle):
        """Draw the weapon with unique appearance for each type."""
        if self.is_melee:
            # Draw knife as a line
            knife_length = 20
            end_x = x + math.cos(angle) * knife_length
            end_y = y + math.sin(angle) * knife_length
            # Draw blade
            pygame.draw.line(screen, (192, 192, 192), (x, y), (end_x, end_y), 3)
            # Draw handle
            handle_x = x + math.cos(angle) * 8
            handle_y = y + math.sin(angle) * 8
            pygame.draw.line(screen, (101, 67, 33), (x, y), (handle_x, handle_y), 5)
        else:
            # Base gun properties
            gun_color = (80, 80, 80)  # Default dark gray
            barrel_width = 3
            grip_length = 12
            grip_width = 6

            if self.type == WeaponType.PISTOL:
                gun_length = 25
                barrel_width = 3
                # Draw slide
                slide_length = 18
                slide_height = 5
                slide_x = x + math.cos(angle) * slide_length
                slide_y = y + math.sin(angle) * slide_length
                pygame.draw.line(
                    screen, (60, 60, 60), (x, y), (slide_x, slide_y), slide_height
                )
                # Draw barrel
                barrel_x = x + math.cos(angle) * gun_length
                barrel_y = y + math.sin(angle) * gun_length
                pygame.draw.line(
                    screen, gun_color, (x, y), (barrel_x, barrel_y), barrel_width
                )

            elif self.type == WeaponType.SHOTGUN:
                gun_length = 40
                barrel_width = 5
                # Draw double barrel
                offset = 2
                perp_x = math.cos(angle + math.pi / 2) * offset
                perp_y = math.sin(angle + math.pi / 2) * offset
                barrel1_end_x = x + math.cos(angle) * gun_length + perp_x
                barrel1_end_y = y + math.sin(angle) * gun_length + perp_y
                barrel2_end_x = x + math.cos(angle) * gun_length - perp_x
                barrel2_end_y = y + math.sin(angle) * gun_length - perp_y
                pygame.draw.line(
                    screen,
                    gun_color,
                    (x + perp_x, y + perp_y),
                    (barrel1_end_x, barrel1_end_y),
                    3,
                )
                pygame.draw.line(
                    screen,
                    gun_color,
                    (x - perp_x, y - perp_y),
                    (barrel2_end_x, barrel2_end_y),
                    3,
                )
                # Draw pump
                pump_length = 25
                pump_x = x + math.cos(angle) * pump_length
                pump_y = y + math.sin(angle) * pump_length
                pygame.draw.line(screen, (100, 100, 100), (x, y), (pump_x, pump_y), 6)

            elif self.type == WeaponType.SMG:
                gun_length = 30
                # Draw compact body
                body_x = x + math.cos(angle) * gun_length
                body_y = y + math.sin(angle) * gun_length
                pygame.draw.line(screen, gun_color, (x, y), (body_x, body_y), 4)
                # Draw magazine well at an angle
                mag_angle = angle + math.pi / 4
                mag_length = 12
                mag_x = x + math.cos(mag_angle) * mag_length
                mag_y = y + math.sin(mag_angle) * mag_length
                pygame.draw.line(screen, (70, 70, 70), (x, y), (mag_x, mag_y), 5)

            elif self.type == WeaponType.ASSAULT_RIFLE:
                gun_length = 45
                # Draw long barrel
                barrel_x = x + math.cos(angle) * gun_length
                barrel_y = y + math.sin(angle) * gun_length
                pygame.draw.line(screen, gun_color, (x, y), (barrel_x, barrel_y), 3)
                # Draw carry handle/sight
                sight_length = 8
                sight_offset = 15
                sight_start_x = x + math.cos(angle) * sight_offset
                sight_start_y = y + math.sin(angle) * sight_offset
                sight_angle = angle - math.pi / 2
                sight_end_x = sight_start_x + math.cos(sight_angle) * sight_length
                sight_end_y = sight_start_y + math.sin(sight_angle) * sight_length
                pygame.draw.line(
                    screen,
                    (50, 50, 50),
                    (sight_start_x, sight_start_y),
                    (sight_end_x, sight_end_y),
                    3,
                )

            elif self.type == WeaponType.BATTLE_RIFLE:
                gun_length = 50
                # Draw long heavy barrel
                barrel_x = x + math.cos(angle) * gun_length
                barrel_y = y + math.sin(angle) * gun_length
                pygame.draw.line(screen, gun_color, (x, y), (barrel_x, barrel_y), 4)
                # Draw scope
                scope_length = 12
                scope_offset = 20
                scope_start_x = x + math.cos(angle) * scope_offset
                scope_start_y = y + math.sin(angle) * scope_offset
                scope_angle = angle - math.pi / 2
                scope_end_x = scope_start_x + math.cos(scope_angle) * scope_length
                scope_end_y = scope_start_y + math.sin(scope_angle) * scope_length
                pygame.draw.line(
                    screen,
                    (40, 40, 40),
                    (scope_start_x, scope_start_y),
                    (scope_end_x, scope_end_y),
                    4,
                )
                # Draw bipod
                bipod_length = 8
                bipod_angle1 = angle + math.pi / 4
                bipod_angle2 = angle - math.pi / 4
                bipod_x = x + math.cos(angle) * gun_length
                bipod_y = y + math.sin(angle) * gun_length
                pygame.draw.line(
                    screen,
                    (60, 60, 60),
                    (bipod_x, bipod_y),
                    (
                        bipod_x + math.cos(bipod_angle1) * bipod_length,
                        bipod_y + math.sin(bipod_angle1) * bipod_length,
                    ),
                    2,
                )
                pygame.draw.line(
                    screen,
                    (60, 60, 60),
                    (bipod_x, bipod_y),
                    (
                        bipod_x + math.cos(bipod_angle2) * bipod_length,
                        bipod_y + math.sin(bipod_angle2) * bipod_length,
                    ),
                    2,
                )

            # Draw grip for all guns (except melee)
            grip_angle = angle + math.pi * 3 / 4
            grip_x = x + math.cos(grip_angle) * grip_length
            grip_y = y + math.sin(grip_angle) * grip_length
            pygame.draw.line(screen, (40, 40, 40), (x, y), (grip_x, grip_y), grip_width)

    def set_game(self, game):
        """Set the game reference for this weapon."""
        self.game = game
