import pygame
from typing import Union, List, Tuple, Callable, Any, overload

class Button_Base:
    NORMAL_STATE: int = 0
    HOVERED_STATE: int = 1
    PRESSED_STATE: int = 2
    def __init__(self, size: Union[List[int], Tuple[int]], position: Union[List[int], Tuple[int]], callback: Callable[[], Any] = None) -> None:
        self.size = size
        self.position = position
        self.callback = callback
        self.rect: pygame.Rect = pygame.Rect(self.position, self.size)

        self.state = Button_Base.NORMAL_STATE

        self.mouse_info = {"button_pressed": False, "button_down": False, "button_up": False, "inside_rect": False}

    def handle_events(self, event: pygame.Event) -> None:
        self.mouse_info["button_pressed"] = False
        self.mouse_info["button_up"] = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_info["button_pressed"] = True
            self.mouse_info["button_down"] = True
        if event.type == pygame.MOUSEBUTTONUP:
            self.mouse_info["button_up"] = True
            self.mouse_info["button_down"] = False
    
    def update_state(self) -> None:
        if (self.mouse_info["button_pressed"] and self.mouse_info["inside_rect"]) or (self.state == Button_Base.PRESSED_STATE and self.mouse_info["button_down"]):
            self.state = Button_Base.PRESSED_STATE
            return
        
        if self.mouse_info["inside_rect"]:
            self.state = self.HOVERED_STATE
            return
    
        self.state = Button_Base.NORMAL_STATE
    
    def render(self) -> Any:
        return NotImplementedError
    
    def update(self) -> None:
        mouse_position = pygame.mouse.get_pos()
        self.mouse_info["inside_rect"] = self.rect.collidepoint(mouse_position)

        if self.mouse_info["button_up"] and self.mouse_info["inside_rect"] and self.state == Button_Base.PRESSED_STATE:
            if self.callback: self.callback()

        self.update_state()

        
class Text_Button(Button_Base):
    def __init__(self, position: Union[List[int], Tuple[int]], text: str, normal_color: pygame.Color, 
                 hover_color: pygame.Color, pressed_color: pygame.Color,
                 font: pygame.Font, callback: Callable[[], Any] = None) -> None:
        
        self.colors = {
            Button_Base.NORMAL_STATE: normal_color,
            Button_Base.HOVERED_STATE: hover_color,
            Button_Base.PRESSED_STATE: pressed_color
        }
        self.current_color = self.colors[Button_Base.NORMAL_STATE]
        self.font = font
        self.text = text
        self.text_surface = self.font.render(self.text, True, self.current_color)
        super().__init__(self.text_surface.get_size(), position, callback)
    
    def render(self, render_surface: pygame.Surface) -> None:
        render_surface.blit(self.text_surface, self.rect)
    
    def update(self) -> None:
        new_color = self.colors[self.state]
        if new_color != self.current_color:
            self.current_color = new_color
            self.text_surface = self.font.render(self.text, True, self.current_color)
        return super().update()
