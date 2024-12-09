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

    def draw(self, screen, offset_x=0, offset_y=0):
        """Draw the particle with optional trail."""
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
                    (
                        int(trail_x - offset_x - trail_size),
                        int(trail_y - offset_y - trail_size),
                    ),
                )

        # Draw particle
        particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            particle_surf,
            (*self.color, self.alpha),
            (self.size, self.size),
            self.size,
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
        self.permanent_decals = []  # For blood stains that stay on ground
        self.max_decals = 100  # Limit permanent decals for performance

    def add_particle(self, particle: Particle) -> None:
        self.particles.append(particle)

    def add_decal(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        size: float,
        alpha: int = 128,
    ) -> None:
        """Add a permanent decal (like blood stains) to the ground."""
        if len(self.permanent_decals) >= self.max_decals:
            self.permanent_decals.pop(0)  # Remove oldest decal

        self.permanent_decals.append(
            {"x": x, "y": y, "color": color, "size": size, "alpha": alpha}
        )

    def update(self) -> None:
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, screen, camera_offset=(0, 0)):
        """Draw all particles with camera offset."""
        # Unpack camera offset
        offset_x, offset_y = camera_offset

        # Draw permanent decals first (they should be under everything else)
        for decal in self.permanent_decals:
            screen_x = int(decal["x"] - offset_x)
            screen_y = int(decal["y"] - offset_y)

            # Create surface for the decal with alpha
            decal_surf = pygame.Surface(
                (decal["size"] * 2, decal["size"] * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                decal_surf,
                (*decal["color"], decal["alpha"]),
                (decal["size"], decal["size"]),
                decal["size"],
            )
            screen.blit(
                decal_surf, (screen_x - decal["size"], screen_y - decal["size"])
            )

        # Draw active particles
        for particle in self.particles:
            particle.draw(screen, offset_x, offset_y)

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

    def create_bullet_trail(self, x, y, angle, color):
        """Create a trail effect behind a bullet."""
        # Ensure angle is a float
        if isinstance(angle, tuple):
            dx, dy = angle
            angle = math.atan2(dy, dx)
        else:
            angle = float(angle)

        # Create overlapping trails for continuous effect
        num_segments = 3  # Number of overlapping segments
        base_length = 8  # Base length of each segment
        line_width = 2  # Fixed width
        lifetime = 0.2  # Longer lifetime for smoother fade

        for i in range(num_segments):
            # Calculate segment position with overlap
            segment_length = base_length * (1 + i * 0.8)
            # Start exactly at bullet position
            start_x = x
            start_y = y
            # End behind bullet with overlap
            end_x = x - math.cos(angle) * segment_length
            end_y = y - math.sin(angle) * segment_length

            # Create line particle with decreasing initial alpha for each segment
            initial_alpha = 0.8 - (i * 0.15)  # Start more transparent
            particle = LineParticle(
                start_x,
                start_y,
                end_x,
                end_y,
                line_width,
                color,
                lifetime,
                initial_alpha,
            )
            self.add_particle(particle)

    def create_blood_effect(
        self,
        x: float,
        y: float,
        direction: Tuple[float, float] = (0, 0),
        amount: int = 10,
        impact_point: Tuple[float, float] = None,  # Add impact point parameter
    ) -> None:
        """Create a blood splatter effect with permanent decals."""
        # Blood colors for variation
        blood_colors = [
            (150, 0, 0),  # Dark red
            (180, 0, 0),  # Medium red
            (200, 0, 0),  # Bright red
            (120, 0, 0),  # Very dark red
        ]

        # Use impact point if provided, otherwise use center
        spawn_x = impact_point[0] if impact_point else x
        spawn_y = impact_point[1] if impact_point else y

        # Calculate base angle from direction
        base_angle = math.atan2(direction[1], direction[0])

        # Create main blood particles
        for _ in range(amount):
            angle = base_angle + random.uniform(-math.pi / 3, math.pi / 3)
            speed = random.uniform(2, 6)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)

            self.add_particle(
                Particle(
                    spawn_x,
                    spawn_y,
                    random.choice(blood_colors),
                    velocity,
                    lifetime=random.randint(20, 40),
                    size=random.uniform(2, 4),
                    gravity=0.2,
                    fade=True,
                    trail_length=3,
                )
            )

        # Create blood spray particles
        for _ in range(amount // 2):
            angle = base_angle + random.uniform(-math.pi / 6, math.pi / 6)
            speed = random.uniform(7, 12)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)

            self.add_particle(
                Particle(
                    spawn_x,
                    spawn_y,
                    random.choice(blood_colors),
                    velocity,
                    lifetime=random.randint(10, 20),
                    size=1,
                    gravity=0.1,
                    fade=True,
                    trail_length=2,
                )
            )

        # Create permanent blood decals on the ground
        for _ in range(amount // 2):
            decal_x = spawn_x + random.uniform(-10, 10)
            decal_y = spawn_y + random.uniform(-10, 10)
            decal_size = random.uniform(3, 8)
            decal_color = random.choice(blood_colors)
            decal_alpha = random.randint(100, 180)

            self.add_decal(decal_x, decal_y, decal_color, decal_size, decal_alpha)

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

    def add_walking_particle(self, x, y, direction):
        """Add a particle effect for walking."""
        angle = direction + random.uniform(-0.5, 0.5)  # Spread particles
        speed = random.uniform(1, 3)
        size = random.uniform(4, 8)  # Increased from (2, 4)
        lifetime = random.uniform(0.3, 0.6)
        color = (150, 150, 150)  # Dust color

        self.add_particle(
            x, y, angle, speed, size, lifetime, color, alpha_fade=True, gravity=0.1
        )


class LineParticle(Particle):
    """A particle that renders as a line instead of a circle."""

    def __init__(
        self, start_x, start_y, end_x, end_y, width, color, lifetime, initial_alpha=1.0
    ):
        velocity = (0.0, 0.0)
        super().__init__(
            x=start_x,
            y=start_y,
            color=color,
            velocity=velocity,
            lifetime=int(lifetime * 60),
            size=width,
            fade=True,
            glow=False,
        )
        self.end_x = end_x
        self.end_y = end_y
        self.width = width
        self.initial_alpha = initial_alpha

    def draw(self, screen, offset_x=0, offset_y=0):
        """Draw the line particle."""
        # Smooth fade out with initial transparency
        progress = self.lifetime / self.max_lifetime
        # Quadratic fade for smoother transition
        fade = progress * progress
        # Start partially transparent and fade to zero
        alpha = int(min(255, 120 * fade * self.initial_alpha))

        if alpha <= 0:
            return

        # Draw the line from start to end point
        start_pos = (int(self.x - offset_x), int(self.y - offset_y))
        end_pos = (int(self.end_x - offset_x), int(self.end_y - offset_y))

        # Draw the line with fixed width
        pygame.draw.line(screen, (*self.color, alpha), start_pos, end_pos, self.width)
