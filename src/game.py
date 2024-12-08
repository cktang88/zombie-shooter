import pygame
from .entities.player import Player
from .entities.castle import Castle
from .managers.wave_manager import WaveManager
from .managers.shop_manager import ShopManager
from .utils.game_state import GameState
import math
import random


class Game:
    """
    Game Manager - Core Game Logic
    -----------------------------

    This class manages the main game loop and state transitions. It handles:

    1. Game States:
       - PLAYING: Active gameplay with zombies and shooting
       - SHOPPING: Between waves, player can buy upgrades
       - PAUSED: Game paused, can resume or quit

    2. Core Systems:
       - Camera management with smooth following and screen shake
       - Sprite group management (bullets, zombies, structures)
       - Wave management and progression
       - Shop system between waves
       - Player and castle (base) management

    3. Rendering:
       - Layered rendering (background -> structures -> zombies -> player -> bullets -> UI)
       - UI elements (health, ammo, wave info, cash)
       - Screen shake effects
       - Shop interface

    4. Coordinate Systems:
       - Screen coordinates: Relative to viewport
       - World coordinates: Absolute positions in game world
       - Conversion methods between the two

    5. Game Flow:
       - Wave starts -> Players fights zombies
       - Wave complete -> Shop opens
       - Player buys upgrades -> Next wave starts
    """

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))

        # Game state
        self.state = GameState.SHOPPING
        self.is_paused = False
        self.cash = 500

        # World dimensions
        self.world_width = screen_width * 2
        self.world_height = screen_height * 2

        # Camera position
        self.camera_x = 0
        self.camera_y = 0

        # Screen shake
        self.screen_shake_amount = 0
        self.screen_shake_decay = 0.9  # How quickly the shake reduces
        self.screen_shake_intensity = 8  # Base intensity of shake

        # Initialize sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.structures = pygame.sprite.Group()
        self.grenades = pygame.sprite.Group()

        # Initialize game objects
        self.player = Player(screen_width // 4, screen_height // 2, self)
        self.castle = Castle(100, screen_height // 2)
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.castle)

        # Initialize managers
        self.wave_manager = WaveManager()
        self.shop_manager = ShopManager(self)

        # Game clock
        self.clock = pygame.time.Clock()

        # Mouse state
        self.mouse_world_x = 0
        self.mouse_world_y = 0

    def add_screen_shake(self, intensity=1.0):
        """Add screen shake effect with given intensity multiplier."""
        self.screen_shake_amount = self.screen_shake_intensity * intensity

    def update_screen_shake(self):
        """Update screen shake effect."""
        if self.screen_shake_amount > 0:
            # Apply random offset to camera
            shake_offset_x = random.randint(
                -int(self.screen_shake_amount), int(self.screen_shake_amount)
            )
            shake_offset_y = random.randint(
                -int(self.screen_shake_amount), int(self.screen_shake_amount)
            )
            self.camera_x += shake_offset_x
            self.camera_y += shake_offset_y
            # Decay the shake amount
            self.screen_shake_amount *= self.screen_shake_decay
            # Cut off small values to stop
            if self.screen_shake_amount < 0.1:
                self.screen_shake_amount = 0

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates."""
        return screen_x + self.camera_x, screen_y + self.camera_y

    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates."""
        return world_x - self.camera_x, world_y - self.camera_y

    def update(self):
        # Update mouse world coordinates
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.mouse_world_x, self.mouse_world_y = self.screen_to_world(mouse_x, mouse_y)

        # Update shop manager
        self.shop_manager.update()

        if not self.is_paused and self.state == GameState.PLAYING:
            # Update player with world coordinates
            self.player.update(self.mouse_world_x, self.mouse_world_y)

            # Update all sprites and check collisions
            for bullet in list(self.bullets):
                bullet.update()

                # Check for zombie collisions using the smaller collision rect
                for zombie in list(self.zombies):
                    if bullet.collision_rect.colliderect(zombie.rect):
                        zombie.take_damage(bullet.damage)
                        bullet.kill()
                        break

                # Remove bullets that are off screen
                if (
                    bullet.rect.right < self.camera_x
                    or bullet.rect.left > self.camera_x + self.screen_width
                    or bullet.rect.bottom < self.camera_y
                    or bullet.rect.top > self.camera_y + self.screen_height
                ):
                    bullet.kill()

            self.zombies.update(self.player.rect.centerx, self.player.rect.centery)
            self.structures.update()

            # Update grenades and handle explosions
            for grenade in list(self.grenades):
                grenade.update()
                if grenade.exploded:
                    # Check for zombies in explosion radius
                    for zombie in self.zombies:
                        dx = zombie.rect.centerx - grenade.rect.centerx
                        dy = zombie.rect.centery - grenade.rect.centery
                        distance = math.sqrt(dx * dx + dy * dy)

                        if distance <= grenade.explosion_radius:
                            # Calculate damage falloff based on distance
                            damage_multiplier = 1 - (
                                distance / grenade.explosion_radius
                            )
                            damage = grenade.explosion_damage * damage_multiplier
                            zombie.take_damage(int(damage))

                    # Add explosion effect (screen shake)
                    self.add_screen_shake(2.0)  # Stronger shake for explosions

                    # Remove the exploded grenade
                    grenade.kill()

            # Update wave manager
            self.wave_manager.update(self)

            # Check for wave completion
            if self.wave_manager.wave_complete():
                self.state = GameState.SHOPPING
                print("Wave complete! Entering shop...")  # Debug

            # Update camera to follow player with smoothing
            target_x = max(
                0,
                min(
                    self.player.rect.centerx - self.screen_width // 2,
                    self.world_width - self.screen_width,
                ),
            )
            target_y = max(
                0,
                min(
                    self.player.rect.centery - self.screen_height // 2,
                    self.world_height - self.screen_height,
                ),
            )

            # Smooth camera movement with lower smoothing factor
            self.camera_x += (target_x - self.camera_x) * 0.05  # Reduced from 0.1
            self.camera_y += (target_y - self.camera_y) * 0.05  # Reduced from 0.1

            # Update screen shake
            self.update_screen_shake()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == GameState.PLAYING:
                    self.is_paused = not self.is_paused
                elif self.state == GameState.SHOPPING:
                    # Don't allow leaving shop without starting next wave
                    pass

        # Don't handle other events if paused
        if self.is_paused:
            return True

        # Let shop manager handle events first when shopping
        if self.state == GameState.SHOPPING:
            if self.shop_manager.handle_event(event):
                return True

        # Let player handle events (shooting, weapon switching, etc.)
        if self.state == GameState.PLAYING:
            # Update mouse world coordinates
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.mouse_world_x, self.mouse_world_y = self.screen_to_world(
                mouse_x, mouse_y
            )

            # Let player handle the event
            if self.player.handle_event(event):
                return True

        return True

    def draw_game_objects(self):
        """Draw all game objects in the correct order."""
        # Draw world border
        border_rect = pygame.Rect(
            -self.camera_x, -self.camera_y, self.world_width, self.world_height
        )
        pygame.draw.rect(self.screen, (50, 100, 50), border_rect, 3)

        # Draw castle first (it's the most background element)
        self.castle.draw(
            self.screen,
            self.castle.rect.x - self.camera_x,
            self.castle.rect.y - self.camera_y,
        )

        # Draw structures
        for structure in self.structures:
            structure.draw(
                self.screen,
                structure.rect.x - self.camera_x,
                structure.rect.y - self.camera_y,
            )

        # Draw zombies
        for zombie in self.zombies:
            zombie.draw(
                self.screen,
                zombie.rect.x - self.camera_x,
                zombie.rect.y - self.camera_y,
            )

        # Draw player
        self.player.draw(
            self.screen,
            self.player.rect.x - self.camera_x,
            self.player.rect.y - self.camera_y,
        )

        # Draw bullets on top
        for bullet in self.bullets:
            screen_x = bullet.rect.x - self.camera_x
            screen_y = bullet.rect.y - self.camera_y
            bullet.draw(self.screen, screen_x, screen_y)

        # Draw grenades and their explosion radius preview last
        for grenade in self.grenades:
            grenade.draw(
                self.screen,
                grenade.rect.x - self.camera_x,
                grenade.rect.y - self.camera_y,
            )

            # Draw explosion radius preview if grenade hasn't exploded
            if not grenade.exploded:
                pygame.draw.circle(
                    self.screen,
                    (255, 200, 0, 128),  # Semi-transparent yellow
                    (
                        int(grenade.rect.centerx - self.camera_x),
                        int(grenade.rect.centery - self.camera_y),
                    ),
                    int(grenade.explosion_radius),
                    1,  # Draw only outline
                )

    def draw_ui(self):
        """Draw all UI elements."""
        # Draw UI background panel
        ui_panel = pygame.Surface((200, 150))
        ui_panel.fill((40, 40, 40))  # Dark gray
        ui_panel.set_alpha(200)  # Semi-transparent
        self.screen.blit(ui_panel, (5, 5))

        # Draw UI text with improved contrast
        font = pygame.font.Font(None, 36)

        # Draw cash with background
        cash_text = font.render(f"Cash: ${self.cash}", True, (34, 255, 34))
        self.screen.blit(cash_text, (15, 15))

        # Draw wave information
        wave_text = font.render(
            f"Wave: {self.wave_manager.current_wave}", True, (255, 255, 255)
        )
        self.screen.blit(wave_text, (15, 55))

        # Draw remaining zombies
        zombies_text = font.render(
            f"Zombies: {len(self.zombies)}", True, (255, 255, 255)
        )
        self.screen.blit(zombies_text, (15, 95))

        # Draw ammo counter
        if self.player.current_weapon:
            if self.player.current_weapon.is_melee:
                ammo_text = font.render("Melee Weapon", True, (255, 255, 255))
            else:
                ammo_text = font.render(
                    f"Ammo: {self.player.current_weapon.current_ammo}/{self.player.current_weapon.ammo_capacity}",
                    True,
                    (255, 255, 255),
                )
            self.screen.blit(ammo_text, (15, 135))

        # Always draw the inventory toolbar
        self.shop_manager.draw_toolbar(self.screen)

        # Draw pause overlay if paused
        if self.is_paused:
            # Semi-transparent overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))

            # Pause text
            font = pygame.font.Font(None, 74)
            pause_text = font.render("PAUSED", True, (255, 255, 255))
            text_rect = pause_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2)
            )
            self.screen.blit(pause_text, text_rect)

            # Instructions
            font = pygame.font.Font(None, 36)
            instruction_text = font.render("Press ESC to resume", True, (200, 200, 200))
            instruction_rect = instruction_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 + 50)
            )
            self.screen.blit(instruction_text, instruction_rect)

    def draw_zombie_radar(self):
        """Draw radar indicators for off-screen zombies."""
        # Constants for radar appearance
        RADAR_MARGIN = 50  # Distance from screen edge
        DOT_SIZE = 8
        RADAR_COLOR = (255, 50, 50)  # Bright red

        # Calculate viewport bounds
        viewport_left = self.camera_x
        viewport_right = self.camera_x + self.screen_width
        viewport_top = self.camera_y
        viewport_bottom = self.camera_y + self.screen_height

        for zombie in self.zombies:
            # Check if zombie is outside viewport
            is_outside_viewport = (
                zombie.rect.right < viewport_left
                or zombie.rect.left > viewport_right
                or zombie.rect.bottom < viewport_top
                or zombie.rect.top > viewport_bottom
            )

            if is_outside_viewport:
                # Get zombie's position relative to screen center
                screen_center_x = self.screen_width / 2
                screen_center_y = self.screen_height / 2

                # Calculate direction to zombie from screen center
                dx = zombie.rect.centerx - (self.camera_x + screen_center_x)
                dy = zombie.rect.centery - (self.camera_y + screen_center_y)
                angle = math.atan2(dy, dx)

                # Calculate radar dot position along screen edge
                radar_x = screen_center_x + math.cos(angle) * (
                    self.screen_width / 2 - RADAR_MARGIN
                )
                radar_y = screen_center_y + math.sin(angle) * (
                    self.screen_height / 2 - RADAR_MARGIN
                )

                # Clamp to screen edges
                radar_x = max(
                    RADAR_MARGIN, min(self.screen_width - RADAR_MARGIN, radar_x)
                )
                radar_y = max(
                    RADAR_MARGIN, min(self.screen_height - RADAR_MARGIN, radar_y)
                )

                # Calculate distance for scaling
                distance = math.sqrt(dx * dx + dy * dy)
                max_distance = math.sqrt(
                    self.world_width * self.world_width
                    + self.world_height * self.world_height
                )
                scale = 1 - min(distance / max_distance, 0.8)  # Cap minimum size at 20%

                # Draw radar dot with glow effect
                base_size = DOT_SIZE * (
                    0.5 + scale * 0.5
                )  # Scale dot size based on distance

                # Draw outer glow
                for i in range(4, 0, -1):
                    size = int(base_size) + i
                    alpha = int(255 * (1 - i / 4))

                    # Create a surface for this glow layer
                    glow_surf = pygame.Surface((size * 2, size * 2))
                    glow_surf.set_colorkey((0, 0, 0))

                    # Draw the glow circle
                    pygame.draw.circle(glow_surf, RADAR_COLOR, (size, size), size)

                    # Set the alpha for this layer
                    glow_surf.set_alpha(alpha)

                    # Blit the glow layer
                    self.screen.blit(
                        glow_surf, (int(radar_x - size), int(radar_y - size))
                    )

                # Draw core dot (solid color)
                pygame.draw.circle(
                    self.screen,
                    RADAR_COLOR,
                    (int(radar_x), int(radar_y)),
                    max(1, int(base_size) // 2),  # Ensure minimum size of 1
                )

    def draw(self):
        # Clear screen
        self.screen.fill((100, 150, 100))  # Light green background

        # Draw game objects in order (background to foreground)
        self.draw_game_objects()

        # Draw UI elements
        if self.state == GameState.SHOPPING:
            self.shop_manager.draw(self.screen)
        else:
            self.draw_ui()

        # Draw zombie radar
        self.draw_zombie_radar()

        # Update display
        pygame.display.flip()
        self.clock.tick(60)
