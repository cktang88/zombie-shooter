"""
Zombie Entity Module
------------------

This module implements the zombie enemies in the game. It provides:

1. Zombie Types:
   - NORMAL: Balanced zombie (Speed: 2, Health: 100, Damage: 10)
   - FAST: Quick but weak (Speed: 4, Health: 50, Damage: 5)
   - TANK: Slow but tough (Speed: 1, Health: 200, Damage: 20)

2. State Machine:
   - IDLE: Default state when spawned
   - CHASE: Moving towards player
   - ATTACK: Within range to damage player
   - DEAD: Zombie eliminated

3. Behaviors:
   - Pathfinding: Direct line to player
   - Attack: Damage when in range
   - Health System: Takes damage, dies at 0
   - Rewards: Drops cash on death

4. Visual Features:
   - Color-coded by type
   - Health bar display
   - Smooth movement
   - Attack animations

5. Balance:
   - Each type has trade-offs (speed/health/damage)
   - Detection ranges vary by type
   - Cash rewards based on difficulty
"""

import pygame
import math
import random
from enum import Enum


class ZombieType(Enum):
    """Defines different zombie variants with unique stats."""

    NORMAL = 1  # Balanced
    FAST = 2  # Quick but weak
    TANK = 3  # Slow but tough


class ZombieState(Enum):
    """State machine for zombie behavior."""

    IDLE = 1  # Not engaged
    CHASE = 2  # Moving to target
    ATTACK = 3  # Within attack range
    DEAD = 4  # Eliminated


class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y, zombie_type=ZombieType.NORMAL):
        super().__init__()
        self.rect = pygame.Rect(x, y, 32, 32)
        self.x = float(x)
        self.y = float(y)
        self.type = zombie_type
        self.state = ZombieState.CHASE

        # Movement and combat attributes
        self.speed = self.get_type_speed()
        self.health = self.get_type_health()
        self.max_health = self.health
        self.damage = self.get_type_damage()
        self.detection_range = 400
        self.attack_range = 50
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = 0

        # Visual effects
        self.prev_positions = [(self.x, self.y)]  # For trail effect
        self.max_trail_length = 5
        self.glow_radius = 20
        self.base_color = self.get_type_color()

    def get_type_speed(self):
        """Get movement speed based on zombie type."""
        if self.type == ZombieType.FAST:
            return 4
        elif self.type == ZombieType.TANK:
            return 1
        return 2  # NORMAL type

    def get_type_health(self):
        """Get max health based on zombie type."""
        if self.type == ZombieType.FAST:
            return 50
        elif self.type == ZombieType.TANK:
            return 200
        return 100  # NORMAL type

    def get_type_damage(self):
        """Get damage based on zombie type."""
        if self.type == ZombieType.FAST:
            return 5
        elif self.type == ZombieType.TANK:
            return 20
        return 10  # NORMAL type

    def get_type_color(self):
        """Get base color based on zombie type."""
        if self.type == ZombieType.FAST:
            return (255, 100, 100)  # Red
        elif self.type == ZombieType.TANK:
            return (100, 100, 255)  # Blue
        return (0, 255, 0)  # Green for normal

    def update(self, *args):
        """Update zombie position and state."""
        # Move horizontally towards the left side of the screen
        self.rect.x -= self.speed

        # Update trail positions for glow effect
        self.prev_positions.append((self.rect.centerx, self.rect.centery))
        if len(self.prev_positions) > self.max_trail_length:
            self.prev_positions.pop(0)

    def take_damage(self, amount):
        """Apply damage to the zombie."""
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw(self, screen, x, y):
        """Draw the zombie with glow effects and health bar."""
        # Draw glow effect
        center_x = x + self.rect.width // 2
        center_y = y + self.rect.height // 2

        # Draw outer glow
        for r in range(self.glow_radius, 0, -2):
            # Interpolate between base color and lighter version
            factor = r / self.glow_radius
            color = tuple(int(c + (255 - c) * (1 - factor)) for c in self.base_color)
            pygame.draw.circle(screen, color, (center_x, center_y), r)

        # Draw zombie body
        pygame.draw.circle(screen, self.base_color, (center_x, center_y), 16)

        # Draw health bar with gradient
        self.draw_health_bar(screen, x, y)

    def draw_health_bar(self, screen, x, y):
        """Draw health bar with gradient effect."""
        bar_width = self.rect.width
        bar_height = 4
        bar_x = x
        bar_y = y - 10

        # Health bar background with gradient
        for i in range(bar_height):
            color = tuple(int(60 * (1 + i / bar_height)) for _ in range(3))
            pygame.draw.line(
                screen, color, (bar_x, bar_y + i), (bar_x + bar_width, bar_y + i)
            )

        # Health bar fill with gradient
        if self.health > 0:
            health_width = int(bar_width * (self.health / self.max_health))

            # Create glow surface
            glow_surf = pygame.Surface(
                (health_width + 4, bar_height + 4), pygame.SRCALPHA
            )

            # Draw glow
            pygame.draw.rect(
                glow_surf, (255, 0, 0, 50), (0, 0, health_width + 4, bar_height + 4)
            )
            screen.blit(glow_surf, (bar_x - 2, bar_y - 2))

            # Draw health fill
            pygame.draw.rect(
                screen, (255, 0, 0), (bar_x, bar_y, health_width, bar_height)
            )
