"""
Turret Structures Module
----------------------

This module implements defensive turrets that automatically shoot at zombies.
"""

import pygame
import math
from .structure import Structure
from ..weapons.weapon import Bullet


class Turret(Structure):
    def __init__(self, x, y, damage, fire_rate, range):
        super().__init__(x, y, 32, 32, 150)  # Turrets are 32x32 with 150 health
        self.damage = damage
        self.fire_rate = fire_rate  # Shots per second
        self.range = range
        self.target = None
        self.last_shot_time = 0
        self.angle = 0
        self.draw_turret()

    def draw_turret(self):
        """Draw the base turret appearance."""
        # Draw base
        pygame.draw.circle(self.image, (100, 100, 100), (16, 16), 16)
        # Draw barrel mount
        pygame.draw.circle(self.image, (80, 80, 80), (16, 16), 8)

    def update(self, game):
        """Update turret state and shoot at zombies."""
        current_time = pygame.time.get_ticks()

        # Find nearest zombie in range
        nearest_dist = float("inf")
        self.target = None

        for zombie in game.zombies:
            dist = math.hypot(
                zombie.rect.centerx - self.rect.centerx,
                zombie.rect.centery - self.rect.centery,
            )
            if dist <= self.range and dist < nearest_dist:
                nearest_dist = dist
                self.target = zombie

        # Update angle and shoot if we have a target
        if self.target and current_time - self.last_shot_time > 1000 / self.fire_rate:
            self.angle = math.atan2(
                self.target.rect.centery - self.rect.centery,
                self.target.rect.centerx - self.rect.centerx,
            )
            self.shoot(game)
            self.last_shot_time = current_time

    def shoot(self, game):
        """Create a bullet and add it to the game."""
        bullet = Bullet(self.rect.centerx, self.rect.centery, self.angle, self.damage)
        game.bullets.add(bullet)

    def draw(self, screen, x, y):
        """Draw turret with rotating barrel."""
        # Draw base sprite
        super().draw(screen, x, y)

        # Draw barrel
        barrel_length = 20
        end_x = x + 16 + math.cos(self.angle) * barrel_length
        end_y = y + 16 + math.sin(self.angle) * barrel_length
        pygame.draw.line(screen, (60, 60, 60), (x + 16, y + 16), (end_x, end_y), 4)


class BasicTurret(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, damage=10, fire_rate=1, range=200)  # 1 shot per second
        self.image.fill((50, 50, 200))  # Blue color
        self.draw_turret()


class AdvancedTurret(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, damage=15, fire_rate=2, range=300)  # 2 shots per second
        self.image.fill((100, 100, 255))  # Lighter blue
        self.draw_turret()

    def draw_turret(self):
        """Draw advanced turret with enhanced appearance."""
        super().draw_turret()
        # Add extra details
        pygame.draw.circle(self.image, (150, 150, 255), (16, 16), 12, 2)  # Extra ring
        pygame.draw.circle(self.image, (200, 200, 255), (16, 16), 6, 1)  # Center detail
