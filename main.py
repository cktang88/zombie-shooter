import pygame
import sys
from src.game import Game

def main():
    # Initialize Pygame
    pygame.init()
    pygame.font.init()
    
    # Set up the display
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    pygame.display.set_caption("Zombie Defense Shooter")
    
    # Create game instance
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Game loop
    clock = pygame.time.Clock()
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key in [pygame.K_SPACE, pygame.K_p]:
                    game.toggle_pause()
            
            # Pass events to game
            game.handle_event(event)
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw()
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)

if __name__ == "__main__":
    main()
