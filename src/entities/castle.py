import pygame

class Castle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 80, 120)  # Castle size
        self.health = 1000
        self.max_health = 1000
        self.color = (150, 150, 150)  # Gray castle
    
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.kill()
    
    def draw(self, screen, x, y):
        # Draw castle body
        castle_rect = pygame.Rect(x, y, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, self.color, castle_rect)
        
        # Draw castle details
        # Windows
        window_size = 15
        window_margin = 10
        for row in range(3):
            for col in range(2):
                window_x = x + window_margin + col * (window_size + window_margin)
                window_y = y + window_margin + row * (window_size + window_margin)
                pygame.draw.rect(screen, (100, 100, 200),  # Blue windows
                               (window_x, window_y, window_size, window_size))
        
        # Draw battlements
        battlement_width = 20
        battlement_height = 15
        num_battlements = self.rect.width // battlement_width
        for i in range(num_battlements):
            pygame.draw.rect(screen, self.color,
                           (x + i * battlement_width, y - battlement_height,
                            battlement_width - 2, battlement_height))
        
        # Draw health bar
        bar_width = self.rect.width
        bar_height = 8
        bar_x = x
        bar_y = y - 20
        
        # Health bar background
        pygame.draw.rect(screen, (60, 60, 60),
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Health bar fill
        health_width = int(bar_width * (self.health / self.max_health))
        if health_width > 0:
            pygame.draw.rect(screen, (255, 0, 0),
                           (bar_x, bar_y, health_width, bar_height))
