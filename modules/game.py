import pygame

from .settings_module import Settings

class Game:
    def __init__(self, settings: Settings) -> None:
        pygame.init()
        self.settings = settings
        self.screen = pygame.display.get_surface()
    
    def run(self) -> None:
        pass

