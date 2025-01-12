import pygame
from sys import exit
import os
import cv2
from typing import Any

from .state_module import Game_State_Manager
from .game_states import Main_Menu, Dance_Selection, Play_Dance, Scoreboard
from .dance_module import Dance_Loader
from .video_module import Video_Capture_Handler, Video_Recorder
from .settings_module import Settings

class Game:
    def __init__(self, settings: Settings) -> None:
        pygame.init()
        self.settings = settings
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()

        self.dance_loader = Dance_Loader(self.settings)
        self.dances = self.dance_loader.load_dance_data()
        self.dances = {i: dance for i, dance in enumerate(self.dances)}

        self.state_manager = Game_State_Manager(self.settings)
        self._create_states()
        self.state_manager.set_state(self.settings.state.STATE_MAIN_MENU_KEY)

        self.webcam = Video_Capture_Handler(self.settings.camera.CAMERA_INDEX)
    
    def _quit_game(self) -> None:
        pygame.quit()
        exit()

    def _create_states(self) -> None:
        self.state_manager.add_state(self.settings.state.STATE_MAIN_MENU_KEY, Main_Menu(self.settings))
        self.state_manager.add_state(self.settings.state.STATE_DANCE_SELECTION_KEY, Dance_Selection(self.settings, self.dances))
    
    def _handle_state_manager_returned_value(self, returned_value: str) -> None:
        if returned_value is None: return
        if not isinstance(returned_value, str): return

        if returned_value == self.settings.state.STATE_MAIN_MENU_KEY:
            self.state_manager.set_state(returned_value)
        if returned_value == self.settings.state.STATE_DANCE_SELECTION_KEY:
            self.state_manager.set_state(returned_value)
        
        if returned_value.startswith(self.settings.state.PLAY_DANCE_KEY):
            dance_id = returned_value.split(self.settings.state.PLAY_DANCE_KEY_SPLIT_CHARACTHER)[1]
            dance_id = int(dance_id)
            if dance_id in self.dances:
                dance = self.dances[dance_id]
                self.state_manager.add_state(self.settings.state.STATE_PLAY_DANCE_KEY, Play_Dance(self.settings, dance, self.webcam))
                self.state_manager.set_state(self.settings.state.STATE_PLAY_DANCE_KEY)
        
        if returned_value.startswith(self.settings.state.DANCE_SCORE_KEY):
            score = returned_value.split(self.settings.state.DANCE_SCORE_KEY_SPLIT_CHARACTHER)[1]
            print("Score:", score)
            self.state_manager.add_state(self.settings.state.STATE_SCOREBOARD_KEY, Scoreboard(self.settings, score))
            self.state_manager.set_state(self.settings.state.STATE_SCOREBOARD_KEY)

        if returned_value == self.settings.state.QUIT_KEY:
            self._quit_game()
    
    def run(self) -> None:
        while True:
            dt = self.clock.tick(self.settings.display.FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit_game()
                
                self.state_manager.handle_events(event)
            
            returned_value = self.state_manager.update(dt)
            self._handle_state_manager_returned_value(returned_value)
            self.state_manager.render(self.screen)

            pygame.display.update()

