"""
Grenade Weapons Module
--------------------

This module implements throwable weapons including grenades and molotovs.
"""

import pygame
import math


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.rect = pygame.Rect(x, y, 10, 10)
        self.x = float(x)
        self.y = float(y)
        self.dx = dx
        self.dy = dy
        self.speed = 10
        self.explosion_radius = 100
        self.damage = 100
        self.exploded = False
        self.explosion_time = None
        self.explosion_duration = 500  # ms

    def update(self, current_time):
        if not self.exploded:
            self.x += self.dx * self.speed
            self.y += self.dy * self.speed
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
        elif current_time - self.explosion_time > self.explosion_duration:
            self.kill()

    def explode(self, current_time):
        self.exploded = True
        self.explosion_time = current_time

    def draw(self, screen, x, y):
        if not self.exploded:
            pygame.draw.circle(screen, (100, 100, 100), (x + 5, y + 5), 5)
        else:
            # Draw explosion effect
            alpha = int(
                255
                * (
                    1
                    - (pygame.time.get_ticks() - self.explosion_time)
                    / self.explosion_duration
                )
            )
            if alpha > 0:
                explosion_surf = pygame.Surface(
                    (self.explosion_radius * 2, self.explosion_radius * 2),
                    pygame.SRCALPHA,
                )
                pygame.draw.circle(
                    explosion_surf,
                    (*self.get_explosion_color(), alpha),
                    (self.explosion_radius, self.explosion_radius),
                    self.explosion_radius,
                )
                screen.blit(
                    explosion_surf,
                    (x - self.explosion_radius, y - self.explosion_radius),
                )

    def get_explosion_color(self):
        return (255, 200, 0)  # Yellow explosion


class MolotovGrenade(Grenade):
    def __init__(self, x, y, dx, dy):
        super().__init__(x, y, dx, dy)
        self.explosion_radius = 80
        self.damage = 50  # Less immediate damage
        self.fire_duration = 5000  # Fire lasts 5 seconds
        self.fire_damage = 20  # Damage per second to zombies in fire
        self.fire_particles = []
        self.last_particle_time = 0
        self.particle_spawn_delay = 100  # ms between particle spawns

    def update(self, current_time):
        if not self.exploded:
            super().update(current_time)
        else:
            # Update fire particles
            if current_time - self.explosion_time <= self.fire_duration:
                if current_time - self.last_particle_time > self.particle_spawn_delay:
                    self.spawn_fire_particles()
                    self.last_particle_time = current_time

            # Update existing particles
            for particle in self.fire_particles[:]:
                particle["life"] -= 1
                if particle["life"] <= 0:
                    self.fire_particles.remove(particle)
                else:
                    particle["y"] -= particle["speed"]  # Fire rises
                    particle["x"] += particle["dx"]

            if (
                current_time - self.explosion_time > self.fire_duration
                and not self.fire_particles
            ):
                self.kill()

    def spawn_fire_particles(self):
        """Create new fire particles at random positions within the fire area."""
        import random

        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.explosion_radius)
            particle_x = self.x + math.cos(angle) * distance
            particle_y = self.y + math.sin(angle) * distance
            self.fire_particles.append(
                {
                    "x": particle_x,
                    "y": particle_y,
                    "dx": random.uniform(-0.5, 0.5),
                    "speed": random.uniform(0.5, 1.5),
                    "size": random.randint(3, 8),
                    "life": random.randint(20, 40),
                    "color": random.choice(
                        [
                            (255, 100, 0),  # Orange
                            (255, 50, 0),  # Red-orange
                            (255, 200, 0),  # Yellow
                        ]
                    ),
                }
            )

    def draw(self, screen, x, y):
        if not self.exploded:
            # Draw molotov bottle
            pygame.draw.rect(screen, (200, 100, 50), (x, y, 10, 15))
            # Draw rag
            pygame.draw.line(screen, (150, 150, 150), (x + 5, y), (x + 5, y - 5), 2)
        else:
            # Draw fire area indicator
            alpha = min(
                128,
                int(
                    128
                    * (
                        1
                        - (pygame.time.get_ticks() - self.explosion_time)
                        / self.fire_duration
                    )
                ),
            )
            if alpha > 0:
                fire_area = pygame.Surface(
                    (self.explosion_radius * 2, self.explosion_radius * 2),
                    pygame.SRCALPHA,
                )
                pygame.draw.circle(
                    fire_area,
                    (255, 100, 0, alpha),
                    (self.explosion_radius, self.explosion_radius),
                    self.explosion_radius,
                )
                screen.blit(
                    fire_area, (x - self.explosion_radius, y - self.explosion_radius)
                )

            # Draw fire particles
            for particle in self.fire_particles:
                screen_x = int(particle["x"] - self.x + x)
                screen_y = int(particle["y"] - self.y + y)
                size = particle["size"]
                color = particle["color"]

                # Draw particle with glow
                glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                glow_center = (size * 2, size * 2)

                # Draw outer glow
                for radius in range(size * 2, size - 1, -1):
                    alpha = int(100 * (radius - size) / (size))
                    pygame.draw.circle(glow_surf, (*color, alpha), glow_center, radius)

                # Draw core
                pygame.draw.circle(glow_surf, color, glow_center, size)

                # Position glow surface
                screen.blit(glow_surf, (screen_x - size * 2, screen_y - size * 2))

    def get_explosion_color(self):
        return (255, 100, 0)  # Orange explosion
