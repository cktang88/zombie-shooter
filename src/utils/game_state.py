from enum import Enum

class GameState(Enum):
    MENU = 1
    SHOPPING = 2
    PLAYING = 3
    PAUSED = 4
    GAME_OVER = 5
