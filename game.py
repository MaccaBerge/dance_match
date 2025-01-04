import pygame

from settings import Settings

class Game:
    def __init__(self, settings: Settings) -> None:
        pygame.init()
        self.settings = settings
        self.screen = pygame.display.get_surface()

