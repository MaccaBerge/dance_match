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
    """
    The Game class initializes and manages the game loop, handles state transitions,
    manages game data (like dances and webcam capture), and interacts with game components.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initializes the game by setting up Pygame, loading dance data, initializing game states,
        and configuring webcam capture.
        
        Args:
            settings (Settings): The configuration settings that dictate various game parameters.
        """
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
        """
        Quits the game by shutting down Pygame and exiting the program.
        """
        self.webcam.release()
        pygame.quit() 
        exit()  

    def _create_states(self) -> None:
        """
        Adds the initial game states (main menu and dance selection) to the state manager.
        """
        self.state_manager.add_state(self.settings.state.STATE_MAIN_MENU_KEY, Main_Menu(self.settings))
        self.state_manager.add_state(self.settings.state.STATE_DANCE_SELECTION_KEY, Dance_Selection(self.settings, self.dances))
    
    def _handle_state_manager_returned_value(self, returned_value: str) -> None:
        """
        Handles the state returned by the state manager. It updates the current game state based on the returned value.
        
        Args:
            returned_value (str): The identifier of the state to switch to or an action to perform.
        """
        if returned_value is None:
            return
        if not isinstance(returned_value, str):
            return

        # Handle main menu state
        if returned_value == self.settings.state.STATE_MAIN_MENU_KEY:
            self.state_manager.set_state(returned_value)
        
        # Handle dance selection state
        if returned_value == self.settings.state.STATE_DANCE_SELECTION_KEY:
            self.state_manager.set_state(returned_value)
        
        # Handle play dance state (triggered when the user selects a dance to play)
        if returned_value.startswith(self.settings.state.PLAY_DANCE_KEY):
            dance_id = returned_value.split(self.settings.state.PLAY_DANCE_KEY_SPLIT_CHARACTHER)[1]
            dance_id = int(dance_id) 
            if dance_id in self.dances:
                dance = self.dances[dance_id] 
                self.state_manager.add_state(self.settings.state.STATE_PLAY_DANCE_KEY, Play_Dance(self.settings, dance, self.webcam))
                self.state_manager.set_state(self.settings.state.STATE_PLAY_DANCE_KEY)
        
        if returned_value.startswith(self.settings.state.DANCE_SCORE_KEY):
            score = returned_value.split(self.settings.state.DANCE_SCORE_KEY_SPLIT_CHARACTHER)[1]
            self.state_manager.add_state(self.settings.state.STATE_SCOREBOARD_KEY, Scoreboard(self.settings, score))
            self.state_manager.set_state(self.settings.state.STATE_SCOREBOARD_KEY)

        if returned_value == self.settings.state.QUIT_KEY:
            self._quit_game()
    
    def run(self) -> None:
        """
        Main game loop. This continuously processes events, updates the game state,
        renders the screen, and controls the frame rate.
        """
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
