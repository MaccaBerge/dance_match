import pygame

from .state_module import Game_State

class Main_Menu(Game_State):
    def __init__(self) -> None:
        super().__init__()
    
    def handle_events(self, event: pygame.Event) -> None:
        pass

    def render(self, render_surface: pygame.Surface) -> None:
        pass
    
    def update(self, dt: float) -> None:
        pass