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
        # Initialize available shop items
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
        self.inventory = []  # Player's purchased items
        self.selected_item = None  # Currently selected item
        self.placing_item = False  # Whether player is placing an item
        self.font = pygame.font.Font(None, 36)

    def update(self):
        """
        Update shop state and item availability.
        Checks player cash and enables/disables items.
        """
        # Update enabled states based on cash
        for item in self.shop_items:
            item.enabled = self.game.cash >= item.cost

        # Handle item placement
        if self.placing_item and self.selected_item:
            mouse_pos = pygame.mouse.get_pos()
            world_x = mouse_pos[0] + self.game.camera_x
            world_y = mouse_pos[1] + self.game.camera_y

            # Check if position is valid (not colliding with other structures)
            can_place = True
            temp_rect = pygame.Rect(world_x - 20, world_y - 20, 40, 40)
            for structure in self.game.structures:
                if temp_rect.colliderect(structure.rect):
                    can_place = False
                    break

            # Place item on click
            if pygame.mouse.get_pressed()[0] and can_place:
                new_structure = self.selected_item.item_class(world_x, world_y)
                self.game.structures.add(new_structure)
                self.game.all_sprites.add(new_structure)
                self.inventory.remove(self.selected_item)
                self.selected_item = None
                self.placing_item = False

    def handle_event(self, event):
        """
        Handle mouse and keyboard events for shop interaction.
        Returns True if event was handled.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Handle start wave button
            button_width = 200
            button_height = 50
            button_x = (self.game.screen_width - button_width) // 2
            button_y = self.game.screen_height - 150  # Above toolbar
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

            if button_rect.collidepoint(mouse_pos):
                self.game.state = GameState.PLAYING
                self.game.wave_manager.start_next_wave()  # Start the next wave
                return True

            # Handle shop items
            if event.button == 1:  # Left click
                item_spacing = 120
                start_x = (
                    self.game.screen_width - (len(self.shop_items) * item_spacing)
                ) // 2
                start_y = 100

                # Check shop items
                for i, item in enumerate(self.shop_items):
                    item_rect = pygame.Rect(
                        start_x + (i * item_spacing), start_y, 100, 100
                    )
                    if item_rect.collidepoint(mouse_pos) and item.enabled:
                        if self.game.cash >= item.cost:
                            self.game.cash -= item.cost
                            self.inventory.append(item)
                            return True

                # Check inventory items
                toolbar_y = self.game.screen_height - 60
                for i, item in enumerate(self.inventory):
                    item_rect = pygame.Rect(10 + i * 70, toolbar_y + 5, 60, 50)
                    if item_rect.collidepoint(mouse_pos):
                        self.selected_item = item
                        self.placing_item = True
                        return True

            elif event.button == 3:  # Right click
                self.selected_item = None
                self.placing_item = False
                return True

        elif event.type == pygame.KEYDOWN:
            # Number keys 1-9 for quick selection
            if event.key in range(pygame.K_1, pygame.K_9 + 1):
                index = event.key - pygame.K_1
                if index < len(self.inventory):
                    self.selected_item = self.inventory[index]
                    self.placing_item = True
                    return True
            # G key to cycle through grenades
            elif event.key == pygame.K_g:
                self.cycle_grenades()
                return True

        return False

    def cycle_grenades(self):
        """Cycle through available grenades in inventory."""
        grenade_items = [
            item
            for item in self.inventory
            if issubclass(item.item_class, (Grenade, MolotovGrenade))
        ]
        if not grenade_items:
            return

        if self.selected_item not in grenade_items:
            self.selected_item = grenade_items[0]
        else:
            current_index = grenade_items.index(self.selected_item)
            next_index = (current_index + 1) % len(grenade_items)
            self.selected_item = grenade_items[next_index]
        self.placing_item = True

    def draw_shop_overlay(self, screen):
        """
        Draw the shop interface overlay.
        Shows available items, prices, and inventory.
        """
        # Draw semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.fill((230, 240, 255))  # Light blue background
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        # Draw shop title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("SHOP", True, (50, 50, 150))
        title_rect = title.get_rect(centerx=screen.get_width() // 2, y=20)
        screen.blit(title, title_rect)

        # Draw available cash
        cash_text = self.font.render(f"Cash: ${self.game.cash}", True, (34, 139, 34))
        cash_rect = cash_text.get_rect(topright=(screen.get_width() - 20, 20))
        screen.blit(cash_text, cash_rect)

        # Draw items in a grid
        item_spacing = 120
        start_x = (screen.get_width() - (len(self.shop_items) * item_spacing)) // 2
        start_y = 100

        for i, item in enumerate(self.shop_items):
            x = start_x + (i * item_spacing)
            item_rect = pygame.Rect(x, start_y, 100, 100)

            # Draw item card
            pygame.draw.rect(screen, (255, 255, 255), item_rect, border_radius=10)
            pygame.draw.rect(screen, (200, 210, 255), item_rect, 2, border_radius=10)

            # Draw item preview using actual graphics
            if item.preview_image:
                preview_rect = item.preview_image.get_rect(
                    center=(x + 50, start_y + 40)
                )
                screen.blit(item.preview_image, preview_rect)

            # Draw item name
            name_font = pygame.font.Font(None, 24)
            name_text = name_font.render(item.name, True, (50, 50, 150))
            name_rect = name_text.get_rect(centerx=x + 50, y=start_y + 75)
            screen.blit(name_text, name_rect)

            # Draw cost
            cost_text = name_font.render(
                f"${item.cost}", True, (34, 139, 34) if item.enabled else (200, 0, 0)
            )
            cost_rect = cost_text.get_rect(centerx=x + 50, y=start_y + 90)
            screen.blit(cost_text, cost_rect)

            # Draw hover effect
            mouse_pos = pygame.mouse.get_pos()
            if item_rect.collidepoint(mouse_pos):
                if item.enabled:
                    pygame.draw.rect(
                        screen, (180, 200, 255), item_rect, 3, border_radius=10
                    )
                else:
                    pygame.draw.rect(
                        screen, (255, 100, 100), item_rect, 3, border_radius=10
                    )

        # Draw start wave button
        self.draw_start_wave_button(screen)

        # Draw inventory toolbar
        self.draw_toolbar(screen)

        # Draw placement preview
        if self.placing_item and self.selected_item:
            mouse_pos = pygame.mouse.get_pos()
            if self.selected_item.preview_image:
                preview_rect = self.selected_item.preview_image.get_rect(
                    center=mouse_pos
                )
                preview_surf = self.selected_item.preview_image.copy()
                preview_surf.set_alpha(128)
                screen.blit(preview_surf, preview_rect)

    def draw_toolbar(self, screen):
        """
        Draw the inventory toolbar at the bottom of the screen.
        Shows purchased items and selected item.
        """
        # Draw toolbar background
        toolbar_height = 60
        toolbar_y = screen.get_height() - toolbar_height
        pygame.draw.rect(
            screen, (200, 210, 255), (0, toolbar_y, screen.get_width(), toolbar_height)
        )

        # Draw inventory items
        for i, item in enumerate(self.inventory):
            item_rect = pygame.Rect(10 + i * 70, toolbar_y + 5, 60, 50)

            # Draw item background
            pygame.draw.rect(screen, (255, 255, 255), item_rect, border_radius=5)

            # Draw item using preview image
            if item.preview_image:
                preview_rect = item.preview_image.get_rect(
                    center=(item_rect.centerx, item_rect.centery)
                )
                screen.blit(item.preview_image, preview_rect)

            # Draw number key hint
            number_font = pygame.font.Font(None, 20)
            number_text = number_font.render(str(i + 1), True, (100, 100, 100))
            number_rect = number_text.get_rect(
                topleft=(item_rect.x + 2, item_rect.y + 2)
            )
            screen.blit(number_text, number_rect)

            # Highlight selected item
            if item == self.selected_item:
                pygame.draw.rect(screen, (255, 215, 0), item_rect, 2, border_radius=5)

    def draw_start_wave_button(self, screen):
        """Draw the start wave button with shadow and hover effects."""
        button_width = 200
        button_height = 50
        button_x = (screen.get_width() - button_width) // 2
        button_y = screen.get_height() - 150  # Above toolbar

        # Draw button shadow
        shadow_offset = 3
        pygame.draw.rect(
            screen,
            (80, 180, 80),
            (
                button_x + shadow_offset,
                button_y + shadow_offset,
                button_width,
                button_height,
            ),
            border_radius=25,
        )

        # Draw main button
        pygame.draw.rect(
            screen,
            (100, 200, 100),
            (button_x, button_y, button_width, button_height),
            border_radius=25,
        )
        pygame.draw.rect(
            screen,
            (50, 150, 50),
            (button_x, button_y, button_width, button_height),
            2,
            border_radius=25,
        )

        # Draw button text with shadow
        font = pygame.font.Font(None, 36)
        shadow_text = font.render("Start Wave!", True, (40, 120, 40))
        shadow_rect = shadow_text.get_rect(
            center=(button_x + button_width // 2 + 1, button_y + button_height // 2 + 1)
        )
        screen.blit(shadow_text, shadow_rect)

        text = font.render("Start Wave!", True, (255, 255, 255))
        text_rect = text.get_rect(
            center=(button_x + button_width // 2, button_y + button_height // 2)
        )
        screen.blit(text, text_rect)

    def draw(self, screen):
        """Draw the appropriate shop interface based on game state."""
        if self.game.state == GameState.SHOPPING:
            self.draw_shop_overlay(screen)
        else:
            self.draw_toolbar(screen)
