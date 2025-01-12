import pygame
from sys import exit
import os

from .state_module import Game_State_Manager
from .game_states import Main_Menu, Dance_Selection
from .dance_module import Dance, Dance_Loader
from .pose_module import Pose_Sequence
from .video_module import Video_Capture_Handler
from .settings_module import Settings

class Game:
    def __init__(self, settings: Settings) -> None:
        pygame.init()
        self.settings = settings
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()

        self.dance_loader = Dance_Loader(self.settings)
        self.dances = self.dance_loader.load_dance_data()
        for dance in self.dances:
            print(dance.get_name(), dance.get_pose_sequence(), dance.get_thumbnail(), dance.get_video())

        self.state_manager = Game_State_Manager(self.settings)
        self._create_states()
        self.state_manager.set_state(self.settings.state.MAIN_MENU_KEY)
    
    def _quit_game(self) -> None:
        pygame.quit()
        exit()

    def _create_states(self) -> None:
        self.state_manager.add_state(self.settings.state.MAIN_MENU_KEY, Main_Menu(self.settings))
        self.state_manager.add_state(self.settings.state.DANCE_SELECTION_KEY, Dance_Selection(self.settings, self.dances))
    
    def run(self) -> None:
        while True:
            dt = self.clock.tick(self.settings.display.FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit_game()
                
                self.state_manager.handle_events(event)
            
            if self.state_manager.update(dt) == self.settings.state.QUIT_KEY:
                self._quit_game()
            self.state_manager.render(self.screen)

            pygame.display.update()

