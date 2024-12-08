import pygame
import sys
from src.game import Game


def main():
    pygame.init()

    # Set up the display (larger screen)
    screen_width = 1280
    screen_height = 800

    # Create game instance
    game = Game(screen_width, screen_height)

    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)

        # Update game state
        game.update()

        # Draw everything
        game.draw()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
