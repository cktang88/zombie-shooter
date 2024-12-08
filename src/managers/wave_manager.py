"""
Wave Manager
-----------

This class manages the zombie wave spawning system. It provides:

1. Wave Progression:
   - Tracks current wave number
   - Manages wave difficulty scaling
   - Controls wave completion conditions
   - Handles wave transitions

2. Zombie Spawning:
   - Controls zombie spawn timing
   - Manages spawn positions
   - Determines zombie types per wave
   - Handles special and boss wave events

3. Difficulty Scaling:
   - Increases zombies per wave
   - Adjusts special zombie chances
   - Manages boss wave occurrences
   - Balances spawn delays

4. Wave State:
   - Tracks active zombies
   - Monitors wave completion
   - Manages spawn queues
   - Controls wave pacing
"""

import pygame
import random
from ..entities.zombie import Zombie, ZombieType


class WaveManager:
    def __init__(self):
        # Wave state tracking
        self.current_wave = 0
        self.zombies_to_spawn = 0
        self.spawn_delay = 2000  # ms between spawns
        self.last_spawn_time = 0
        self.wave_complete_flag = False

        # Wave configuration and scaling
        self.base_zombies = 5  # Starting number of zombies
        self.zombies_per_wave = 2  # Additional zombies per wave
        self.special_zombie_chance = 0.2  # 20% chance for special zombies
        self.boss_waves = [5, 10, 15, 20]  # Waves that spawn boss zombies

    def start_next_wave(self):
        """
        Initialize the next wave with scaled difficulty.
        Updates zombie count and resets wave state.
        """
        self.current_wave += 1
        self.zombies_to_spawn = (
            self.base_zombies + (self.current_wave - 1) * self.zombies_per_wave
        )
        print(
            f"Starting wave {self.current_wave} with {self.zombies_to_spawn} zombies"
        )  # Debug
        self.wave_complete_flag = False
        self.last_spawn_time = 0  # Reset spawn timer

    def update(self, game):
        """
        Update wave state and handle zombie spawning.
        Checks wave completion and manages spawn timing.
        """
        from ..game import GameState

        if game.state != GameState.PLAYING or game.is_paused:
            return

        if self.zombies_to_spawn <= 0:
            # Only set wave complete when no zombies are left to spawn AND no active zombies
            if len(game.zombies) == 0:
                self.wave_complete_flag = True
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time > self.spawn_delay:
            self.spawn_zombie(game)
            self.last_spawn_time = current_time

    def spawn_zombie(self, game):
        """
        Spawn a new zombie in the game world.
        Determines position and type based on wave settings.
        """
        # Spawn from right side of world with some margin
        x = game.world_width - 50  # Changed to spawn closer to the visible area
        y = random.randint(50, game.world_height - 50)

        # Determine zombie type
        zombie_type = self.determine_zombie_type()

        # Create and add zombie
        zombie = Zombie(x, y, zombie_type)
        game.zombies.add(zombie)
        print(f"Spawned {zombie_type} zombie at ({x}, {y})")  # Debug

        self.zombies_to_spawn -= 1

    def determine_zombie_type(self):
        """
        Determine the type of zombie to spawn.
        Considers boss waves and special zombie chances.
        """
        if self.current_wave in self.boss_waves:
            return ZombieType.TANK  # Changed BOSS to TANK since BOSS wasn't defined

        if random.random() < self.special_zombie_chance:
            return random.choice([ZombieType.FAST, ZombieType.TANK])

        return ZombieType.NORMAL

    def wave_complete(self):
        """Check if current wave is complete."""
        return self.wave_complete_flag and self.zombies_to_spawn <= 0
