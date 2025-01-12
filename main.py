import pygame

from modules.game import Game
from modules.settings_module import Settings

class Main:
    def __init__(self) -> None:
        pygame.display.set_mode((Settings.display.WIDTH, Settings.display.HEIGHT), vsync=True)

        self.settings = Settings()
        self.game = Game(self.settings)
        
    def run(self) -> None:
        self.game.run()

if __name__ == "__main__":
    main = Main()
    main.run()

