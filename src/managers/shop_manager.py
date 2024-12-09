"""
Shop Manager
-----------

This class manages the in-game shop system. It provides:

1. Shop Interface:
   - Manages shop item display
   - Handles item purchasing
   - Controls shop state
   - Manages inventory system

2. Item Management:
   - Tracks available items
   - Manages item costs
   - Controls item availability
   - Handles item placement

3. Economy System:
   - Tracks player cash
   - Validates purchases
   - Manages refunds
   - Controls pricing

4. UI Rendering:
   - Draws shop interface
   - Renders item previews
   - Shows tooltips
   - Displays inventory
"""

import pygame
import math
from ..structures.structure import Wall
from ..structures.traps import SpikeTrap, SlowTrap
from ..structures.turrets import BasicTurret, AdvancedTurret
from ..weapons.grenades import Grenade, MolotovGrenade
from ..utils.colors import Colors
from ..utils.game_state import GameState


class ShopItem:
    """
    Represents a purchasable item in the shop.
    Contains item metadata and state.
    """

    def __init__(self, name, cost, description, item_class, color):
        self.name = name
        self.cost = cost
        self.description = description
        self.item_class = item_class
        self.color = color
        self.enabled = True
        # Create preview image
        self.preview_image = self.create_preview_image()

    def create_preview_image(self):
        """Create a preview image of the item using its actual appearance."""
        if issubclass(
            self.item_class, (Wall, SpikeTrap, SlowTrap, BasicTurret, AdvancedTurret)
        ):
            # Create instance at 0,0 to get its appearance
            instance = self.item_class(0, 0)
            return instance.image
        elif issubclass(self.item_class, (Grenade, MolotovGrenade)):
            # Create custom preview for grenades
            preview = pygame.Surface((32, 32), pygame.SRCALPHA)
            if self.item_class == Grenade:
                pygame.draw.circle(preview, (100, 100, 100), (16, 16), 8)
            else:  # MolotovGrenade
                # Draw bottle
                pygame.draw.rect(preview, (200, 100, 50), (12, 12, 8, 12))
                # Draw rag
                pygame.draw.line(preview, (150, 150, 150), (16, 12), (16, 8), 2)
            return preview
        return None


class ShopManager:
    def __init__(self, game):
        self.game = game
        self.inventory = []
        self.shop_items = [
            # Defensive Structures
            ShopItem("Wall", 100, "A defensive wall", Wall, (150, 75, 0)),
            ShopItem("Spike Trap", 150, "Damages zombies", SpikeTrap, (200, 50, 50)),
            ShopItem("Slow Trap", 200, "Slows zombies", SlowTrap, (50, 150, 200)),
            ShopItem("Basic Turret", 300, "Auto-shoots", BasicTurret, (50, 50, 200)),
            ShopItem(
                "Adv Turret", 500, "Better turret", AdvancedTurret, (100, 100, 255)
            ),
            # Throwables
            ShopItem("Grenade", 50, "Explodes", Grenade, (100, 100, 100)),
            ShopItem("Molotov", 75, "Fire damage", MolotovGrenade, (200, 100, 50)),
        ]
        self.selected_item = None
        self.placing_item = False
        self.dragging = False
        self.drag_start_pos = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.font = pygame.font.Font(None, 36)

    def handle_event(self, event):
        """Handle mouse and keyboard events for shop interaction."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos

                # Handle start wave button
                if self.game.state == GameState.SHOPPING:
                    button_width = 200
                    button_height = 50
                    button_x = (self.game.screen_width - button_width) // 2
                    button_y = self.game.screen_height - 150  # Above toolbar
                    button_rect = pygame.Rect(
                        button_x, button_y, button_width, button_height
                    )

                    if button_rect.collidepoint(mouse_x, mouse_y):
                        self.game.state = GameState.PLAYING
                        self.game.wave_manager.start_next_wave()
                        return True

                    # Handle shop items purchase
                    item_spacing = 120
                    start_x = (
                        self.game.screen_width - (len(self.shop_items) * item_spacing)
                    ) // 2
                    start_y = 100

                    for i, item in enumerate(self.shop_items):
                        item_rect = pygame.Rect(
                            start_x + (i * item_spacing), start_y, 100, 100
                        )
                        if item_rect.collidepoint(mouse_x, mouse_y):
                            if item.enabled and self.game.cash >= item.cost:
                                self.game.cash -= item.cost
                                self.inventory.append(item)
                                return True

                # Check inventory items
                toolbar_y = self.game.screen_height - 60
                for i, item in enumerate(self.inventory):
                    item_rect = pygame.Rect(10 + i * 70, toolbar_y + 5, 60, 50)
                    if item_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_item = item
                        self.placing_item = True
                        self.dragging = True
                        self.drag_start_pos = (mouse_x, mouse_y)
                        self.drag_offset_x = mouse_x - item_rect.x
                        self.drag_offset_y = mouse_y - item_rect.y
                        return True

            elif event.button == 3:  # Right click
                self.selected_item = None
                self.placing_item = False
                self.dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging and self.selected_item:
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                mouse_x, mouse_y = event.pos
                # Check if the item was dropped in a valid location
                if self.is_valid_placement_location(mouse_x, mouse_y):
                    # Convert screen coordinates to world coordinates
                    world_x = mouse_x + self.game.camera.x
                    world_y = mouse_y + self.game.camera.y

                    # Create and place the item
                    if self.selected_item.item_class:
                        if issubclass(
                            self.selected_item.item_class, (Grenade, MolotovGrenade)
                        ):
                            # For throwables, add to game's projectiles
                            angle = math.atan2(
                                world_y - self.game.player.y,
                                world_x - self.game.player.x,
                            )
                            projectile = self.selected_item.item_class(
                                self.game.player.x, self.game.player.y, angle, self.game
                            )
                            self.game.projectiles.add(projectile)
                        else:
                            # For structures, create and add to game's structures
                            structure = self.selected_item.item_class(
                                world_x, world_y, self.game
                            )
                            self.game.structures.add(structure)

                        # Remove item if it's a one-time use item
                        if issubclass(
                            self.selected_item.item_class, (Grenade, MolotovGrenade)
                        ):
                            self.inventory.remove(self.selected_item)

                self.selected_item = None
                self.placing_item = False
                self.dragging = False
                return True

        elif event.type == pygame.KEYDOWN:
            if event.key in range(pygame.K_1, pygame.K_9 + 1):
                index = event.key - pygame.K_1
                if index < len(self.inventory):
                    self.selected_item = self.inventory[index]
                    self.placing_item = True
                    self.dragging = True
                    return True
            elif event.key == pygame.K_g:
                self.cycle_grenades()
                return True
            elif event.key == pygame.K_ESCAPE:
                if self.placing_item or self.dragging:
                    self.selected_item = None
                    self.placing_item = False
                    self.dragging = False
                    return True

        return False

    def is_valid_placement_location(self, x, y):
        """Check if the current position is valid for item placement."""
        # Don't allow placement in the toolbar area
        if y > self.game.screen_height - 70:
            return False

        # Don't allow placement in shop overlay area during shopping
        if self.game.state == GameState.SHOPPING and y < 250:
            return False

        return True

    def draw_toolbar(self, screen):
        """Draw the inventory toolbar at the bottom of the screen."""
        # Draw toolbar background
        toolbar_height = 60
        toolbar_y = self.game.screen_height - toolbar_height
        pygame.draw.rect(
            screen, (50, 50, 50), (0, toolbar_y, self.game.screen_width, toolbar_height)
        )

        # Draw inventory items
        for i, item in enumerate(self.inventory):
            item_rect = pygame.Rect(10 + i * 70, toolbar_y + 5, 60, 50)

            # Don't draw the item in the toolbar if it's being dragged
            if item != self.selected_item or not self.dragging:
                pygame.draw.rect(screen, (100, 100, 100), item_rect)
                if hasattr(item, "preview_image") and item.preview_image:
                    screen.blit(item.preview_image, item_rect)

                # Draw number key hint
                number_font = pygame.font.Font(None, 20)
                number_text = number_font.render(str(i + 1), True, (200, 200, 200))
                screen.blit(number_text, (item_rect.x + 2, item_rect.y + 2))

        # Draw dragged item
        if self.dragging and self.selected_item:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            drag_rect = pygame.Rect(
                mouse_x - self.drag_offset_x, mouse_y - self.drag_offset_y, 60, 50
            )

            # Draw item preview
            pygame.draw.rect(screen, (100, 100, 100), drag_rect)
            if (
                hasattr(self.selected_item, "preview_image")
                and self.selected_item.preview_image
            ):
                screen.blit(self.selected_item.preview_image, drag_rect)

            # Draw placement indicator
            if self.is_valid_placement_location(mouse_x, mouse_y):
                pygame.draw.rect(screen, (0, 255, 0), drag_rect, 2)
            else:
                pygame.draw.rect(screen, (255, 0, 0), drag_rect, 2)

    def draw(self, screen):
        """Draw shop interface based on game state."""
        if self.game.state == GameState.SHOPPING:
            self.draw_shop_overlay(screen)
        else:
            self.draw_toolbar(screen)

    def draw_shop_overlay(self, screen):
        """Draw the shop interface overlay."""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.fill((230, 240, 255))
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Draw shop title
        title = self.font.render("SHOP", True, (50, 50, 150))
        title_rect = title.get_rect(centerx=screen.get_width() // 2, y=20)
        screen.blit(title, title_rect)

        # Draw available cash
        cash_text = self.font.render(f"Cash: ${self.game.cash}", True, (34, 139, 34))
        screen.blit(cash_text, (screen.get_width() - 150, 20))

        # Draw items grid
        item_spacing = 120
        start_x = (screen.get_width() - (len(self.shop_items) * item_spacing)) // 2
        start_y = 100

        for i, item in enumerate(self.shop_items):
            x = start_x + (i * item_spacing)
            item_rect = pygame.Rect(x, start_y, 100, 100)

            # Draw item card
            pygame.draw.rect(screen, (255, 255, 255), item_rect, border_radius=10)
            if item.enabled:
                color = (200, 210, 255)
            else:
                color = (255, 200, 200)
            pygame.draw.rect(screen, color, item_rect, 2, border_radius=10)

            # Draw item preview
            if hasattr(item, "preview_image") and item.preview_image:
                preview_rect = item.preview_image.get_rect(
                    center=(x + 50, start_y + 40)
                )
                screen.blit(item.preview_image, preview_rect)

            # Draw item name and cost
            name_font = pygame.font.Font(None, 24)
            name_text = name_font.render(item.name, True, (50, 50, 150))
            cost_text = name_font.render(
                f"${item.cost}", True, (34, 139, 34) if item.enabled else (200, 0, 0)
            )
            screen.blit(name_text, (x + 10, start_y + 75))
            screen.blit(cost_text, (x + 10, start_y + 90))

        # Draw start wave button
        button_width = 200
        button_height = 50
        button_x = (screen.get_width() - button_width) // 2
        button_y = screen.get_height() - 150

        pygame.draw.rect(
            screen,
            (100, 200, 100),
            (button_x, button_y, button_width, button_height),
            border_radius=10,
        )

        text = self.font.render("Start Wave!", True, (255, 255, 255))
        text_rect = text.get_rect(
            center=(button_x + button_width // 2, button_y + button_height // 2)
        )
        screen.blit(text, text_rect)

        # Draw toolbar
        self.draw_toolbar(screen)

    def update(self):
        """Update shop state and handle item placement/dragging."""
        # Update enabled states based on cash
        for item in self.shop_items:
            item.enabled = self.game.cash >= item.cost

        # Handle item placement/dragging
        if self.placing_item and self.selected_item:
            mouse_pos = pygame.mouse.get_pos()

            # Convert screen to world coordinates
            world_x = mouse_pos[0] + self.game.camera.x
            world_y = mouse_pos[1] + self.game.camera.y

            # Update placement preview
            if not self.dragging and pygame.mouse.get_pressed()[0]:
                if self.is_valid_placement_location(mouse_pos[0], mouse_pos[1]):
                    if self.selected_item.item_class:
                        if issubclass(
                            self.selected_item.item_class, (Grenade, MolotovGrenade)
                        ):
                            # For throwables, add to game's projectiles
                            angle = math.atan2(
                                world_y - self.game.player.y,
                                world_x - self.game.player.x,
                            )
                            projectile = self.selected_item.item_class(
                                self.game.player.x, self.game.player.y, angle, self.game
                            )
                            self.game.projectiles.add(projectile)

                            # Remove throwable from inventory
                            self.inventory.remove(self.selected_item)
                            self.selected_item = None
                            self.placing_item = False
                        else:
                            # For structures, create and add to game's structures
                            structure = self.selected_item.item_class(
                                world_x, world_y, self.game
                            )
                            self.game.structures.add(structure)

                            # Keep selected for multiple placements
                            if issubclass(
                                self.selected_item.item_class, (Grenade, MolotovGrenade)
                            ):
                                self.inventory.remove(self.selected_item)
                                self.selected_item = None
                                self.placing_item = False
