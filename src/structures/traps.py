"""
Trap Structures Module
--------------------

This module implements various trap structures that damage or slow zombies.
"""

import pygame
from .structure import Structure
from ..ui.ui_helper import Colors


class SpikeTrap(Structure):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, 100)  # 40x40 size, 100 health
        self.damage = 20  # Damage per second
        self.is_active = True
        self.cooldown = 0  # Time until spikes are ready again
        self.cooldown_time = 500  # ms
        self.draw_trap()

    def draw_trap(self):
        """Draw the spike trap appearance."""
        # Draw base
        pygame.draw.rect(
            self.image, Colors.PANEL_BG, (0, 0, self.rect.width, self.rect.height)
        )

        # Draw spikes
        spike_color = (200, 50, 50)
        for i in range(4):
            for j in range(4):
                x = i * 10 + 5
                y = j * 10 + 5
                points = [(x, y + 7), (x + 3, y), (x + 7, y + 7)]
                pygame.draw.polygon(self.image, spike_color, points)

    def update(self, game):
        """Update trap state and damage zombies."""
        current_time = pygame.time.get_ticks()

        # Update cooldown
        if self.cooldown > 0:
            if current_time >= self.cooldown:
                self.cooldown = 0
                self.draw_trap()

        # Check for zombie collisions
        if self.is_active and self.cooldown == 0:
            for zombie in game.zombies:
                if self.rect.colliderect(zombie.rect):
                    # Apply damage (scaled by frame time)
                    zombie.take_damage(self.damage / 60)  # Assuming 60 FPS
                    self.cooldown = current_time + self.cooldown_time
                    self.draw_cooldown()
                    break

    def draw_cooldown(self):
        """Draw the trap in cooldown state."""
        self.image.fill((0, 0, 0, 0))  # Clear
        pygame.draw.rect(
            self.image, Colors.PANEL_BG, (0, 0, self.rect.width, self.rect.height)
        )
        # Draw retracted spikes
        pygame.draw.rect(
            self.image,
            (150, 50, 50),
            (5, 5, self.rect.width - 10, self.rect.height - 10),
        )


class SlowTrap(Structure):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, 100)  # 40x40 size, 100 health
        self.slow_factor = 0.5  # How much to slow zombies (0.5 = half speed)
        self.slow_duration = 2000  # ms
        self.is_active = True
        self.cooldown = 0
        self.cooldown_time = 1000  # ms
        self.affected_zombies = {}  # zombie: end_time
        self.draw_trap()

    def draw_trap(self):
        """Draw the slow trap appearance."""
        # Draw base
        pygame.draw.rect(
            self.image, Colors.PANEL_BG, (0, 0, self.rect.width, self.rect.height)
        )

        # Draw ice crystal pattern
        color = (100, 150, 255)
        # Center crystal
        points = [
            (self.rect.width // 2, 5),
            (self.rect.width - 5, self.rect.height // 2),
            (self.rect.width // 2, self.rect.height - 5),
            (5, self.rect.height // 2),
        ]
        pygame.draw.polygon(self.image, color, points)
        # Draw X pattern
        pygame.draw.line(
            self.image, color, (5, 5), (self.rect.width - 5, self.rect.height - 5), 2
        )
        pygame.draw.line(
            self.image, color, (5, self.rect.height - 5), (self.rect.width - 5, 5), 2
        )

    def update(self, game):
        """Update trap state and slow zombies."""
        current_time = pygame.time.get_ticks()

        # Update cooldown
        if self.cooldown > 0:
            if current_time >= self.cooldown:
                self.cooldown = 0
                self.draw_trap()

        # Update slowed zombies
        zombies_to_remove = []
        for zombie, end_time in self.affected_zombies.items():
            if current_time >= end_time:
                zombie.speed /= self.slow_factor  # Restore speed
                zombies_to_remove.append(zombie)
        for zombie in zombies_to_remove:
            del self.affected_zombies[zombie]

        # Check for new zombie collisions
        if self.is_active and self.cooldown == 0:
            for zombie in game.zombies:
                if zombie not in self.affected_zombies and self.rect.colliderect(
                    zombie.rect
                ):
                    # Slow the zombie
                    zombie.speed *= self.slow_factor
                    self.affected_zombies[zombie] = current_time + self.slow_duration
                    self.cooldown = current_time + self.cooldown_time
                    self.draw_cooldown()
                    break

    def draw_cooldown(self):
        """Draw the trap in cooldown state."""
        self.image.fill((0, 0, 0, 0))  # Clear
        pygame.draw.rect(
            self.image, Colors.PANEL_BG, (0, 0, self.rect.width, self.rect.height)
        )
        # Draw inactive state
        pygame.draw.rect(
            self.image,
            (100, 150, 255, 128),
            (5, 5, self.rect.width - 10, self.rect.height - 10),
        )
