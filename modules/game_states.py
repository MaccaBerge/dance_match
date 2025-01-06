import pygame

from .state_module import Game_State
from .settings_module import Settings

class Main_Menu(Game_State):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings

    def handle_events(self, event: pygame.Event) -> None:
        print("Main Menu (handle events)")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return self.settings.state.DANCE_SELECTION_KEY

    def render(self, render_surface: pygame.Surface) -> None:
        render_surface.fill((255,255,255))
    
    def update(self, dt: float) -> None:
        print("Main Menu (update)")


class Song_Selection(Game_State):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings

    def handle_events(self, event: pygame.Event):
        print("Song Selection (handle events)")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return self.settings.state.MAIN_MENU_KEY
    
    def render(self, render_surface: pygame.Surface) -> None:
        render_surface.fill((100,100,100))
    
    def update(self, dt: float):
        print("Song Selection (update)")