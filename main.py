import pygame

from game import Game
from settings import Settings

class Main:
    def __init__(self) -> None:
        pygame.display.set_mode((Settings.display.WIDTH, Settings.display.HEIGHT))

        self.game = Game()
        
    def run(self) -> None:
        self.game.run()


if __name__ == "__main__":
    main = Main()
    main.run()

