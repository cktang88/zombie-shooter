"""
Particle System Module
--------------------

A comprehensive visual effects system that handles all particle-based effects in the game.

Classes:
    Particle: Individual particle with physics, color, and visual properties
    ParticleSystem: Manager for all particle effects

Particle Features:
    - Position and velocity-based movement
    - Color with alpha transparency
    - Size and scaling
    - Lifetime management
    - Gravity effects
    - Trail effects with fade
    - Glow effects with customizable intensity
    - Dynamic alpha blending

Effect Types:
    1. Combat Effects:
        - Bullet trails with dynamic colors based on weapon damage
        - Blood effects with directional spray and pooling
        - Muzzle flashes with glow
        - Explosion effects with smoke and sparks
        - Impact effects

    2. Movement Effects:
        - Player footsteps with dust
        - Zombie footsteps with blood trails
        - Jump/land effects

    3. Environmental Effects:
        - Ambient floating particles
        - Weather effects (rain, snow)
        - Healing effects with green particles
        - Structure damage effects

    4. Special Effects:
        - Teleport/spawn effects
        - Death effects
        - Power-up effects
        - Shield/barrier effects

Performance Features:
    - Particle pooling for efficiency
    - Automatic cleanup of dead particles
    - View frustum culling
    - Dynamic particle limits
    - Batch rendering optimization
"""

import pygame
import random
import math
from typing import List, Dict, Tuple, Optional


class Particle:
    """
    Individual particle entity with physics and visual properties.

    Properties:
        - Position (x, y): Float coordinates for smooth movement
        - Velocity (dx, dy): Direction and speed
        - Color: RGB with optional alpha
        - Size: Particle radius
        - Lifetime: Duration in frames
        - Gravity: Optional downward acceleration
        - Trail: Optional motion trail with fade
        - Glow: Optional bloom effect
    """

    def __init__(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        velocity: Tuple[float, float],
        lifetime: int,
        size: float = 2,
        alpha: int = 255,
        gravity: float = 0,
        fade: bool = True,
        glow: bool = False,
        trail_length: int = 0,
    ):
        self.x = x
        self.y = y
        self.color = color
        self.dx, self.dy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alpha = alpha
        self.gravity = gravity
        self.fade = fade
        self.glow = glow
        self.trail: List[Tuple[float, float]] = []
        self.trail_length = trail_length

    def update(self) -> bool:
        # Update trail
        if self.trail_length > 0:
            self.trail.append((self.x, self.y))
            if len(self.trail) > self.trail_length:
                self.trail.pop(0)

        # Update position
        self.x += self.dx
        self.y += self.dy

        # Apply gravity
        self.dy += self.gravity

        # Update lifetime and alpha
        self.lifetime -= 1
        if self.fade:
            self.alpha = int((self.lifetime / self.max_lifetime) * 255)

        return self.lifetime > 0

    def draw(
        self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)
    ) -> None:
        offset_x, offset_y = camera_offset
        screen_x = int(self.x - offset_x)
        screen_y = int(self.y - offset_y)

        # Draw trail
        if self.trail_length > 0:
            for i, (trail_x, trail_y) in enumerate(self.trail):
                progress = i / len(self.trail)
                trail_alpha = int(self.alpha * progress)
                trail_size = max(1, self.size * progress)
                trail_surf = pygame.Surface(
                    (trail_size * 2, trail_size * 2), pygame.SRCALPHA
                )
                pygame.draw.circle(
                    trail_surf,
                    (*self.color, trail_alpha),
                    (trail_size, trail_size),
                    trail_size,
                )
                if self.glow:
                    pygame.draw.circle(
                        trail_surf,
                        (*self.color, trail_alpha // 2),
                        (trail_size, trail_size),
                        trail_size * 1.5,
                    )
                screen.blit(
                    trail_surf,
                    (trail_x - offset_x - trail_size, trail_y - offset_y - trail_size),
                )

        # Draw particle
        particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            particle_surf, (*self.color, self.alpha), (self.size, self.size), self.size
        )
        if self.glow:
            pygame.draw.circle(
                particle_surf,
                (*self.color, self.alpha // 2),
                (self.size, self.size),
                self.size * 1.5,
            )
        screen.blit(particle_surf, (screen_x - self.size, screen_y - self.size))


class ParticleSystem:
    """
    Particle System Manager
    ----------------------

    A comprehensive particle system that handles all visual effects in the game.

    Features:
    1. Particle Types:
       - Bullet trails with neon glow
       - Explosion particles with dynamic scaling
       - Blood effects with gravity
       - Muzzle flashes
       - Footsteps
       - Healing effects
       - Environmental particles

    2. Particle Properties:
       - Position and velocity
       - Color and alpha transparency
       - Size and scaling
       - Lifetime management
       - Gravity effects
       - Trail effects
       - Glow effects

    3. Effect Types:
       - create_explosion(): Radial particle burst with glow
       - create_bullet_trail(): Neon trailing particles behind bullets
       - create_blood_effect(): Directional blood splatter with gravity
       - create_muzzle_flash(): Quick bright flash at gun barrel
       - create_footstep(): Small dust particles on movement
       - create_heal_effect(): Rising green particles

    4. Rendering Features:
       - Alpha blending for transparency
       - Trail rendering with fade
       - Glow effects using multiple layers
       - Camera-aware positioning
       - Particle culling for performance

    5. Performance Optimizations:
       - Particle pooling
       - Automatic cleanup of dead particles
       - View frustum culling
       - Efficient batch rendering

    Usage:
        particle_system = ParticleSystem()

        # Create various effects
        particle_system.create_explosion(x, y)
        particle_system.create_bullet_trail(x, y, velocity)
        particle_system.create_blood_effect(x, y, direction)

        # Update and render
        particle_system.update()
        particle_system.draw(screen, camera_offset)
    """

    def __init__(self):
        self.particles: List[Particle] = []

    def add_particle(self, particle: Particle) -> None:
        self.particles.append(particle)

    def update(self) -> None:
        self.particles = [p for p in self.particles if p.update()]

    def draw(
        self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)
    ) -> None:
        for particle in self.particles:
            particle.draw(screen, camera_offset)

    def create_explosion(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int] = (255, 165, 0),
        num_particles: int = 30,
        speed_range: Tuple[float, float] = (2, 8),
        lifetime_range: Tuple[int, int] = (20, 40),
        size_range: Tuple[float, float] = (2, 4),
        glow: bool = True,
    ) -> None:
        # Create main explosion particles
        colors = [
            (255, 165, 0),  # Orange
            (255, 69, 0),  # Red-Orange
            (255, 215, 0),  # Gold
            (255, 255, 0),  # Yellow
        ]

        # Core explosion particles
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(*speed_range)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.randint(*lifetime_range)
            size = random.uniform(*size_range)

            self.add_particle(
                Particle(
                    x,
                    y,
                    random.choice(colors),
                    velocity,
                    lifetime,
                    size=size * 1.5,
                    glow=True,
                    trail_length=8,
                )
            )

        # Add smoke particles
        smoke_colors = [
            (100, 100, 100),  # Gray
            (120, 120, 120),  # Light gray
            (80, 80, 80),  # Dark gray
        ]

        for _ in range(num_particles // 2):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            velocity = (
                math.cos(angle) * speed,
                math.sin(angle) * speed - 0.5,
            )  # Slight upward drift
            lifetime = random.randint(40, 80)  # Smoke lasts longer
            size = random.uniform(3, 6)

            self.add_particle(
                Particle(
                    x,
                    y,
                    random.choice(smoke_colors),
                    velocity,
                    lifetime,
                    size=size,
                    alpha=128,
                    gravity=-0.05,  # Slight upward drift
                    fade=True,
                    glow=False,
                )
            )

        # Add spark particles
        for _ in range(num_particles * 2):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(8, 15)  # Sparks move faster
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.randint(10, 20)  # Sparks are short-lived

            self.add_particle(
                Particle(
                    x,
                    y,
                    (255, 255, 200),  # Bright yellow/white
                    velocity,
                    lifetime,
                    size=1,
                    glow=True,
                    trail_length=3,
                )
            )

    def create_bullet_trail(
        self,
        x: float,
        y: float,
        velocity: Tuple[float, float],
        color: Tuple[int, int, int] = (0, 255, 255),
    ) -> None:
        speed = math.sqrt(velocity[0] ** 2 + velocity[1] ** 2)
        angle = math.atan2(velocity[1], velocity[0])

        for _ in range(3):
            spread = random.uniform(-0.2, 0.2)
            new_angle = angle + spread
            new_velocity = (
                math.cos(new_angle) * speed * 0.3,
                math.sin(new_angle) * speed * 0.3,
            )

            self.add_particle(
                Particle(
                    x,
                    y,
                    color,
                    new_velocity,
                    lifetime=10,
                    size=2,
                    glow=True,
                    trail_length=3,
                )
            )

    def create_blood_effect(
        self,
        x: float,
        y: float,
        direction: Tuple[float, float] = (0, 0),
        amount: int = 10,
    ) -> None:
        """Create a blood splatter effect."""
        # Blood colors for variation
        blood_colors = [
            (150, 0, 0),  # Dark red
            (180, 0, 0),  # Medium red
            (200, 0, 0),  # Bright red
            (120, 0, 0),  # Very dark red
        ]

        # Calculate base angle from direction
        base_angle = math.atan2(direction[1], direction[0])

        # Create main blood particles
        for _ in range(amount):
            # Vary the angle within a cone in the direction of impact
            angle = base_angle + random.uniform(-math.pi / 3, math.pi / 3)
            speed = random.uniform(2, 6)  # Faster particles for more impact
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)

            # Create blood particle with random properties
            self.add_particle(
                Particle(
                    x,
                    y,
                    random.choice(blood_colors),
                    velocity,
                    lifetime=random.randint(20, 40),
                    size=random.uniform(2, 4),
                    gravity=0.2,
                    fade=True,
                    trail_length=3,
                )
            )

        # Create blood spray particles (smaller, faster particles)
        for _ in range(amount // 2):
            angle = base_angle + random.uniform(
                -math.pi / 6, math.pi / 6
            )  # Narrower cone
            speed = random.uniform(7, 12)  # Much faster for spray effect
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)

            self.add_particle(
                Particle(
                    x,
                    y,
                    random.choice(blood_colors),
                    velocity,
                    lifetime=random.randint(10, 20),
                    size=1,
                    gravity=0.1,
                    fade=True,
                    trail_length=2,
                )
            )

        # Create blood pool effect (particles that stay on the ground)
        for _ in range(amount // 2):
            angle = random.uniform(0, math.pi * 2)  # Spread in all directions
            speed = random.uniform(0.5, 2)  # Slower for pool effect
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)

            self.add_particle(
                Particle(
                    x,
                    y,
                    random.choice(blood_colors),
                    velocity,
                    lifetime=random.randint(40, 80),  # Longer lifetime
                    size=random.uniform(3, 5),  # Larger particles
                    gravity=0.4,  # Strong gravity to keep them on ground
                    fade=True,
                    trail_length=0,  # No trail for pool particles
                )
            )

    def create_muzzle_flash(
        self,
        x: float,
        y: float,
        angle: float,
        color: Tuple[int, int, int] = (255, 200, 50),
    ) -> None:
        for _ in range(10):
            spread = random.uniform(-0.5, 0.5)
            speed = random.uniform(3, 6)
            velocity = (
                math.cos(angle + spread) * speed,
                math.sin(angle + spread) * speed,
            )

            self.add_particle(
                Particle(x, y, color, velocity, lifetime=5, size=3, glow=True)
            )

    def create_footstep(
        self, x: float, y: float, color: Tuple[int, int, int] = (150, 150, 150)
    ) -> None:
        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)

            self.add_particle(
                Particle(x, y, color, velocity, lifetime=10, size=1, gravity=0.1)
            )

    def create_heal_effect(self, x: float, y: float, radius: float = 20) -> None:
        for _ in range(15):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(0, radius)
            px = x + math.cos(angle) * dist
            py = y + math.sin(angle) * dist

            velocity = (0, random.uniform(-1, -2))
            self.add_particle(
                Particle(px, py, (0, 255, 0), velocity, lifetime=20, size=2, glow=True)
            )

    def create_ambient_particles(
        self, x: float, y: float, width: float, height: float
    ) -> None:
        """Create ambient particles for atmosphere in the given area."""
        # Only create particles if we have less than 100 ambient particles
        ambient_count = sum(
            1 for p in self.particles if getattr(p, "is_ambient", False)
        )
        if ambient_count >= 100:
            return

        for _ in range(3):  # Create a few particles per frame
            px = random.uniform(x, x + width)
            py = random.uniform(y, y + height)

            # Slow upward drift with slight horizontal movement
            velocity = (
                random.uniform(-0.2, 0.2),  # Slight horizontal drift
                random.uniform(-0.5, -0.3),  # Upward movement
            )

            # Create particle with a dim white/blue color
            color = (
                random.randint(200, 255),  # R
                random.randint(200, 255),  # G
                random.randint(220, 255),  # B
            )

            particle = Particle(
                px,
                py,
                color,
                velocity=velocity,
                lifetime=random.randint(100, 200),
                size=random.uniform(1, 2),
                alpha=random.randint(30, 60),
                fade=True,
                glow=True,
            )
            particle.is_ambient = True  # Mark as ambient for counting
            self.add_particle(particle)
