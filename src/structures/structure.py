"""
Base Structure Class
------------------

This class provides the foundation for all game structures like walls, turrets, and traps.
It handles:
- Basic sprite functionality
- Health and damage system
- Drawing with position adjustment
- Health bar rendering
"""

import pygame
import math


class Structure(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, health):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = health
        self.max_health = health

    def take_damage(self, amount):
        """Apply damage to the structure and destroy if health reaches 0."""
        self.health -= amount
        if self.health <= 0:
            self.kill()

    def draw(self, screen, x, y):
        """
        Draw the structure at the given screen coordinates.

        Args:
            screen: Target surface to draw on
            x, y: Screen coordinates to draw at
        """
        # Draw structure
        screen.blit(self.image, (x, y))

        # Draw health bar
        pygame.draw.rect(screen, (255, 0, 0), (x, y - 5, self.rect.width, 3))
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            (x, y - 5, self.rect.width * (self.health / self.max_health), 3),
        )


class Wall(Structure):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 60, 200)
        self.image.fill((100, 100, 100))


class Trap(Structure):
    def __init__(self, x, y, damage, slow_factor=1.0):
        super().__init__(x, y, 32, 32, 50)
        self.damage = damage
        self.slow_factor = slow_factor
        self.last_damage_time = 0
        self.damage_cooldown = 500  # ms

    def affect_zombie(self, zombie, current_time):
        if current_time - self.last_damage_time >= self.damage_cooldown:
            zombie.take_damage(self.damage)
            self.last_damage_time = current_time
        zombie.speed *= self.slow_factor


class SpikeTrap(Trap):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 1.0)
        self.image.fill((150, 150, 150))
        # Draw spikes
        pygame.draw.lines(
            self.image, (200, 200, 200), False, [(8, 24), (16, 8), (24, 24)], 2
        )


class SlowTrap(Trap):
    def __init__(self, x, y):
        super().__init__(x, y, 5, 0.5)  # Low damage but 50% slow
        self.image.fill((0, 150, 150))
        # Draw slow symbol
        pygame.draw.circle(self.image, (0, 200, 200), (16, 16), 8, 2)


class Turret(Structure):
    def __init__(self, x, y, damage, fire_rate, range):
        super().__init__(x, y, 24, 24, 100)
        self.damage = damage
        self.fire_rate = fire_rate
        self.range = range
        self.target = None
        self.last_shot_time = 0
        self.angle = 0

    def update(self, zombies, bullets, current_time):
        # Find nearest zombie in range
        nearest_dist = float("inf")
        self.target = None

        for zombie in zombies:
            dist = math.hypot(
                zombie.rect.centerx - self.rect.centerx,
                zombie.rect.centery - self.rect.centery,
            )
            if dist <= self.range and dist < nearest_dist:
                nearest_dist = dist
                self.target = zombie

        # Update angle and shoot if we have a target
        if self.target and current_time - self.last_shot_time > self.fire_rate * 1000:
            self.angle = math.atan2(
                self.target.rect.centery - self.rect.centery,
                self.target.rect.centerx - self.rect.centerx,
            )
            self.shoot(bullets)
            self.last_shot_time = current_time

    def shoot(self, bullets):
        from ..weapons.weapon import Bullet

        bullet = Bullet(self.rect.centerx, self.rect.centery, self.angle, self.damage)
        bullets.add(bullet)

    def draw(self, screen):
        super().draw(screen)
        # Draw turret barrel
        end_x = self.rect.centerx + math.cos(self.angle) * 15
        end_y = self.rect.centery + math.sin(self.angle) * 15
        pygame.draw.line(
            screen,
            (50, 50, 50),
            (self.rect.centerx, self.rect.centery),
            (end_x, end_y),
            3,
        )


class BasicTurret(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, 10, 1.0, 200)  # 1 shot per second, range 200
        self.image.fill((0, 0, 255))


class AdvancedTurret(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, 15, 0.5, 300)  # 2 shots per second, range 300
        self.image.fill((0, 0, 200))
