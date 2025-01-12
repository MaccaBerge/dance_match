import pygame
from typing import Union, List, Tuple, Callable, Any

from .utilities_module import apply_tint

class Button_Base:
    """
    A base class for creating interactive buttons with various states.
    """

    # Button states
    NORMAL_STATE: int = 0
    HOVERED_STATE: int = 1
    PRESSED_STATE: int = 2

    def __init__(
        self, 
        size: Union[List[int], Tuple[int]], 
        position: Union[List[int], Tuple[int]], 
        callback: Callable[[], Any] = None
    ) -> None:
        """
        Initialize the button.

        Args:
            size (Union[List[int], Tuple[int]]): The size of the button (width, height).
            position (Union[List[int], Tuple[int]]): The position of the button (x, y).
            callback (Callable[[], Any], optional): The function to call when the button is pressed. Defaults to None.
        """
        self.size: Union[List[int], Tuple[int]] = size
        self.position: Union[List[int], Tuple[int]] = position
        self.callback: Callable[[], Any] = callback
        self.rect: pygame.Rect = pygame.Rect(self.position, self.size)

        self.state: int = Button_Base.NORMAL_STATE

        self.mouse_info: dict[str, bool] = {
            "button_pressed": False, 
            "button_down": False, 
            "button_up": False, 
            "inside_rect": False
        }

    def handle_events(self, event: pygame.event.Event) -> None:
        """
        Handle mouse events and update the mouse_info dictionary.

        Args:
            event (pygame.event.Event): The current event.
        """
        self.mouse_info["button_pressed"] = False
        self.mouse_info["button_up"] = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_info["button_pressed"] = True
            self.mouse_info["button_down"] = True
        if event.type == pygame.MOUSEBUTTONUP:
            self.mouse_info["button_up"] = True
            self.mouse_info["button_down"] = False

    def update_state(self) -> None:
        """
        Update the state of the button based on mouse information.
        """
        if (self.mouse_info["button_pressed"] and self.mouse_info["inside_rect"]) or \
           (self.state == Button_Base.PRESSED_STATE and self.mouse_info["button_down"]):
            self.state = Button_Base.PRESSED_STATE
            return
        
        if self.mouse_info["inside_rect"]:
            self.state = self.HOVERED_STATE
            return

        self.state = Button_Base.NORMAL_STATE

    def render(self) -> Any:
        """
        Render the button. Must be implemented in subclasses.
        """
        raise NotImplementedError

    def update(self) -> None:
        """
        Update the button's state and execute the callback if necessary.
        """
        mouse_position: Tuple[int, int] = pygame.mouse.get_pos()
        self.mouse_info["inside_rect"] = self.rect.collidepoint(mouse_position)

        if self.mouse_info["button_up"] and self.mouse_info["inside_rect"] and self.state == Button_Base.PRESSED_STATE:
            if self.callback:
                self.callback()

        self.update_state()


class Text_Button(Button_Base):
    """
    A button with text that changes color based on its state.
    """

    def __init__(
        self, 
        text: str, 
        position: Union[List[int], Tuple[int]], 
        normal_color: pygame.Color, 
        hover_color: pygame.Color, 
        pressed_color: pygame.Color,
        font: pygame.font.Font, 
        callback: Callable[[], Any] = None
    ) -> None:
        """
        Initialize a Text_Button instance.

        Args:
            text (str): The button's text.
            position (Union[List[int], Tuple[int]]): The position of the button (x, y).
            normal_color (pygame.Color): The color of the button in its normal state.
            hover_color (pygame.Color): The color of the button in its hovered state.
            pressed_color (pygame.Color): The color of the button in its pressed state.
            font (pygame.font.Font): The font for rendering the text.
            callback (Callable[[], Any], optional): The function to call when the button is pressed. Defaults to None.
        """
        self.colors: dict[int, pygame.Color] = {
            Button_Base.NORMAL_STATE: normal_color,
            Button_Base.HOVERED_STATE: hover_color,
            Button_Base.PRESSED_STATE: pressed_color
        }
        self.current_color: pygame.Color = self.colors[Button_Base.NORMAL_STATE]
        self.font: pygame.font.Font = font
        self.text: str = text
        self.text_surface: pygame.Surface = self.font.render(self.text, True, self.current_color)
        super().__init__(self.text_surface.get_size(), position, callback)

    def render(self, render_surface: pygame.Surface) -> None:
        """
        Render the text button on the given surface.

        Args:
            render_surface (pygame.Surface): The surface to render the button on.
        """
        render_surface.blit(self.text_surface, self.rect)

    def update(self) -> None:
        """
        Update the text button's state and appearance.
        """
        new_color: pygame.Color = self.colors[self.state]
        if new_color != self.current_color:
            self.current_color = new_color
            self.text_surface = self.font.render(self.text, True, self.current_color)
        super().update()


class Image_Button(Button_Base):
    """
    A button that uses images for its visual representation.
    """

    def __init__(
        self, 
        image: pygame.Surface, 
        position: Union[List[int], Tuple[int]], 
        hover_tint_color: pygame.Color, 
        pressed_tint_color: pygame.Color,
        hover_tint_intensity: int = 100, 
        pressed_tint_intensity: int = 100,
        callback: Callable[[], Any] = None
    ) -> None:
        """
        Initialize an Image_Button instance.

        Args:
            image (pygame.Surface): The base image for the button.
            position (Union[List[int], Tuple[int]]): The position of the button (x, y).
            hover_tint_color (pygame.Color): The tint color for the hovered state.
            pressed_tint_color (pygame.Color): The tint color for the pressed state.
            hover_tint_intensity (int, optional): The intensity of the hover tint. Defaults to 100.
            pressed_tint_intensity (int, optional): The intensity of the pressed tint. Defaults to 100.
            callback (Callable[[], Any], optional): The function to call when the button is pressed. Defaults to None.
        """
        self.normal_image: pygame.Surface = image
        self.position: Union[List[int], Tuple[int]] = position

        self.hover_image: pygame.Surface = apply_tint(self.normal_image, hover_tint_color, hover_tint_intensity)
        self.pressed_image: pygame.Surface = apply_tint(self.normal_image, pressed_tint_color, pressed_tint_intensity)

        self.images: dict[int, pygame.Surface] = {
            Button_Base.NORMAL_STATE: self.normal_image,
            Button_Base.HOVERED_STATE: self.hover_image,
            Button_Base.PRESSED_STATE: self.pressed_image
        }
        super().__init__(size=self.normal_image.get_size(), position=position, callback=callback)

    def render(self, render_surface: pygame.Surface) -> None:
        """
        Render the image button on the given surface.

        Args:
            render_surface (pygame.Surface): The surface to render the button on.
        """
        render_surface.blit(self.images[self.state], self.rect)

    def update(self) -> None:
        """
        Update the image button's state and appearance.
        """
        super().update()
