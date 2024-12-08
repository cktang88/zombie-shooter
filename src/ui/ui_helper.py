"""
UI Helper
--------

This class provides UI rendering utilities and theme management. It includes:

1. Theme System:
   - Consistent color palette
   - Dark mode optimized colors
   - Accessible contrast ratios
   - Semantic color naming

2. UI Components:
   - Text boxes with backgrounds
   - Progress bars
   - Buttons with hover states
   - Tooltips
   - Panels with transparency
   - Inventory slots

3. Layout Helpers:
   - Centered text rendering
   - Flexible padding system
   - Border radius support
   - Grid-based layouts

4. Visual Effects:
   - Hover highlights
   - Alpha transparency
   - Rounded corners
   - Drop shadows
   - Gradients
"""

import pygame


class Colors:
    """
    Game color theme constants.
    Provides semantic color naming for consistent UI.
    """

    # Main theme colors
    BACKGROUND = (20, 24, 30)  # Dark blue-gray
    PANEL_BG = (30, 34, 40)  # Slightly lighter blue-gray
    TEXT = (220, 220, 220)  # Off-white
    TEXT_SECONDARY = (160, 160, 160)  # Gray
    ACCENT = (65, 195, 165)  # Teal
    ACCENT_DARK = (45, 135, 115)  # Darker teal
    WARNING = (195, 65, 65)  # Red
    HEALTH = (65, 195, 95)  # Green
    AMMO = (195, 165, 65)  # Gold
    CASH = (195, 195, 65)  # Yellow


class UIHelper:
    @staticmethod
    def draw_text_box(
        surface,
        text,
        font,
        color,
        x,
        y,
        padding=10,
        bg_color=Colors.PANEL_BG,
        border_radius=5,
    ):
        """
        Draw text with a background box.

        Args:
            surface: Target surface to draw on
            text: Text string to render
            font: Pygame font object
            color: Text color
            x, y: Position to draw at
            padding: Space around text
            bg_color: Background color
            border_radius: Corner rounding
        """
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        box_rect = pygame.Rect(
            x - padding,
            y - padding,
            text_rect.width + padding * 2,
            text_rect.height + padding * 2,
        )

        # Draw box with rounded corners
        pygame.draw.rect(surface, bg_color, box_rect, border_radius=border_radius)

        # Draw text
        surface.blit(text_surface, (x, y))

        return box_rect

    @staticmethod
    def draw_progress_bar(
        surface,
        x,
        y,
        width,
        height,
        progress,
        color,
        bg_color=Colors.PANEL_BG,
        border_radius=3,
    ):
        """
        Draw a progress bar with background.

        Args:
            surface: Target surface to draw on
            x, y: Position to draw at
            width, height: Bar dimensions
            progress: Value between 0 and 1
            color: Bar fill color
            bg_color: Background color
            border_radius: Corner rounding
        """
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, bg_color, bg_rect, border_radius=border_radius)

        # Progress
        if progress > 0:
            progress_width = int(width * progress)
            progress_rect = pygame.Rect(x, y, progress_width, height)
            pygame.draw.rect(surface, color, progress_rect, border_radius=border_radius)

    @staticmethod
    def draw_panel(surface, rect, bg_color=Colors.PANEL_BG, border_radius=5, alpha=255):
        """
        Draw a panel with optional transparency.

        Args:
            surface: Target surface to draw on
            rect: Panel rectangle
            bg_color: Panel color
            border_radius: Corner rounding
            alpha: Transparency (0-255)
        """
        if alpha < 255:
            # Create a surface with alpha
            panel = pygame.Surface(rect.size, pygame.SRCALPHA)
            panel_color = (*bg_color, alpha)
            pygame.draw.rect(
                panel, panel_color, panel.get_rect(), border_radius=border_radius
            )
            surface.blit(panel, rect)
        else:
            pygame.draw.rect(surface, bg_color, rect, border_radius=border_radius)

    @staticmethod
    def draw_button(
        surface,
        text,
        font,
        rect,
        color=Colors.ACCENT,
        hover_color=Colors.ACCENT_DARK,
        text_color=Colors.TEXT,
        border_radius=5,
    ):
        """
        Draw an interactive button with hover effect.

        Args:
            surface: Target surface to draw on
            text: Button label
            font: Text font
            rect: Button rectangle
            color: Normal button color
            hover_color: Button color when hovered
            text_color: Text color
            border_radius: Corner rounding

        Returns:
            bool: True if button is being hovered
        """
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = rect.collidepoint(mouse_pos)

        # Draw button background
        pygame.draw.rect(
            surface,
            hover_color if is_hovered else color,
            rect,
            border_radius=border_radius,
        )

        # Draw text
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

        return is_hovered

    @staticmethod
    def draw_tooltip(surface, text, font, x, y, padding=10, max_width=200):
        """
        Draw a multi-line tooltip with word wrapping.

        Args:
            surface: Target surface to draw on
            text: Tooltip text
            font: Text font
            x, y: Position to draw at
            padding: Space around text
            max_width: Maximum tooltip width
        """
        # Split text into lines based on max width
        words = text.split()
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            word_surface = font.render(word + " ", True, Colors.TEXT)
            word_width = word_surface.get_width()

            if current_width + word_width > max_width:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width
            else:
                current_line.append(word)
                current_width += word_width

        if current_line:
            lines.append(" ".join(current_line))

        # Calculate tooltip dimensions
        line_height = font.get_linesize()
        tooltip_height = line_height * len(lines) + padding * 2
        tooltip_width = max_width + padding * 2

        # Draw tooltip background
        tooltip_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
        pygame.draw.rect(surface, Colors.PANEL_BG, tooltip_rect, border_radius=5)

        # Draw text lines
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, Colors.TEXT)
            surface.blit(text_surface, (x + padding, y + padding + i * line_height))
