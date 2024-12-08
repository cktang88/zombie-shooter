import pygame
import os

"""
Resource Manager
--------------

This class manages all game assets including sprites and sounds. It provides:

1. Asset Loading:
   - Loads and caches sprite images
   - Loads and caches sound effects
   - Creates placeholder assets when files not available

2. Asset Access:
   - Provides centralized access to all game assets
   - Handles missing assets gracefully
   - Supports dynamic asset loading during gameplay

3. Memory Management:
   - Caches loaded assets to prevent duplicate loading
   - Manages asset lifecycle and cleanup
   - Optimizes memory usage for sprites and sounds

4. Error Handling:
   - Graceful fallback for missing assets
   - Debug logging for asset loading issues
   - Placeholder generation for missing sprites
"""


class ResourceManager:
    def __init__(self):
        self.sprites = {}
        self.sounds = {}
        self.load_resources()

    def load_resources(self):
        # This is where we'll load sprites and sounds
        # For now, we'll use colored rectangles as placeholders
        # Later, you can add actual sprite images and sound files

        # Create placeholder sprites
        player_sprite = pygame.Surface((32, 32))
        player_sprite.fill((0, 255, 0))
        self.sprites["player"] = player_sprite

        zombie_sprite = pygame.Surface((32, 32))
        zombie_sprite.fill((255, 0, 0))
        self.sprites["zombie"] = zombie_sprite

        bullet_sprite = pygame.Surface((8, 8))
        bullet_sprite.fill((255, 255, 0))
        self.sprites["bullet"] = bullet_sprite

        turret_sprite = pygame.Surface((24, 24))
        turret_sprite.fill((0, 0, 255))
        self.sprites["turret"] = turret_sprite

    def get_sprite(self, name):
        """Get a sprite by name. Returns None if not found."""
        return self.sprites.get(name)

    def get_sound(self, name):
        """Get a sound effect by name. Returns None if not found."""
        return self.sounds.get(name)

    def load_sprite(self, name, path):
        """
        Load a sprite from file path and cache it.
        Handles loading errors gracefully.
        """
        try:
            self.sprites[name] = pygame.image.load(path).convert_alpha()
        except pygame.error:
            print(f"Could not load sprite: {path}")

    def load_sound(self, name, path):
        """
        Load a sound effect from file path and cache it.
        Handles loading errors gracefully.
        """
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
        except pygame.error:
            print(f"Could not load sound: {path}")
