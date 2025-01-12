import pygame
from typing import List, Tuple, Any, Union

from .state_module import Game_State
from .button_module import Text_Button
from .dance_module import Dance
from .settings_module import Settings

class Main_Menu(Game_State):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings

        self.font = pygame.Font("fonts/Akira Expanded Demo.otf", 100)
        self.main_menu_text = self.font.render("Dance Match", True, color=(207, 186, 240))
        self.main_menu_text_rect = self.main_menu_text.get_rect(center=(self.settings.display.WIDTH/2, 100))

        self.buttons: List[Text_Button] = []

        self.play_button = Text_Button("Play", (self.settings.display.WIDTH/2, self.settings.display.HEIGHT/2),
                                       normal_color=self.settings.button.NORMAL_COLOR, hover_color=self.settings.button.HOVER_COLOR,
                                       pressed_color=self.settings.button.PRESSED_COLOR, font=self.font, 
                                       callback=lambda: self._button_callback(self.settings.state.DANCE_SELECTION_KEY))
        self.play_button.rect.center = ((self.settings.display.WIDTH/2, self.settings.display.HEIGHT/2))
        self.buttons.append(self.play_button)

        self.quit_button = Text_Button("Quit", (self.settings.display.WIDTH/2, self.settings.display.HEIGHT/2),
                                       normal_color=self.settings.button.NORMAL_COLOR, hover_color=self.settings.button.HOVER_COLOR,
                                       pressed_color=self.settings.button.PRESSED_COLOR, font=self.font, 
                                       callback=lambda: self._button_callback(self.settings.state.QUIT_KEY))
        self.quit_button.rect.center = ((self.settings.display.WIDTH/2, self.settings.display.HEIGHT/2+200))
        self.buttons.append(self.quit_button)

        self.button_callback_queue = []
    
    def _button_callback(self, data: Any) -> None:
        self.button_callback_queue.append(data)

    def handle_events(self, event: pygame.Event) -> None:
        for button in self.buttons:
            button.handle_events(event)

    def render(self, render_surface: pygame.Surface) -> None:
        render_surface.fill((255,255,255))
        render_surface.blit(self.main_menu_text, self.main_menu_text_rect)
        
        for button in self.buttons:
            button.render(render_surface)
    
    def update(self, dt: float) -> None:
        for button in self.buttons:
            button.update()
        
        if self.button_callback_queue: return self.button_callback_queue.pop(0)

class Dance_Selection(Game_State):
    def __init__(self, settings: Settings, dances: Union[List[Dance], Tuple[Dance]]) -> None:
        super().__init__()
        self.settings = settings

    def handle_events(self, event: pygame.Event):
        #print("Song Selection (handle events)")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return self.settings.state.MAIN_MENU_KEY
    
    def render(self, render_surface: pygame.Surface) -> None:
        render_surface.fill((100,100,100))
    
    def update(self, dt: float):
        #print("Song Selection (update)")
        pass