import pygame
from sys import exit

from .state_module import Game_State_Manager
from .game_states import Main_Menu, Song_Selection
from .settings_module import Settings

class Game:
    def __init__(self, settings: Settings) -> None:
        pygame.init()
        self.settings = settings
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()

        self.state_manager = Game_State_Manager(self.settings)
        self._create_states()
        self.state_manager.set_state("main_menu")

    def _create_states(self) -> None:
        self.state_manager.add_state(self.settings.state.MAIN_MENU_KEY, Main_Menu(self.settings))
        self.state_manager.add_state(self.settings.state.DANCE_SELECTION_KEY, Song_Selection(self.settings))
    
    def run(self) -> None:
        while True:
            dt = self.clock.tick(self.settings.display.FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                
                self.state_manager.handle_events(event)
            
            self.state_manager.update(dt)
            self.state_manager.render(self.screen)

            pygame.display.update()

