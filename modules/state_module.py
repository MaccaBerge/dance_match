import pygame
from typing import Any, Dict, Optional

from .settings_module import Settings

class Game_State:
    """Common base class for all game states."""
    def handle_events(self) -> None:
        """Process user input"""
        raise NotImplementedError

    def update(self) -> None:
        """Update state logic."""
        raise NotImplementedError
    
    def render(self) -> None:
        """Render state."""
        raise NotImplementedError


class Game_State_Manager:
    def __init__(self, settings: Settings) -> None:
        self.settings: Settings = settings
        self.states: Dict[str, Game_State] = {}
        self.selected_state: Optional[Game_State] = None

    def _check_selected_state(self) -> None:
        if not self.selected_state:
            raise RuntimeError("No state selected")
        
        if self.selected_state not in self.states:
            raise RuntimeError("The selected state is not a valid state")

    def add_state(self, name: str, state: Game_State) -> None:
        if not isinstance(name, str):
            raise ValueError(f"Invalid tpye for 'name': expected 'str', got {type(name).__name__}")
        if not issubclass(type(state), Game_State):
            raise ValueError(f"Invalid type for 'state': expected subclass of 'Game_State', got {type(state).__name__}")
        
        self.states[name] = state
    
    def set_state(self, name: str) -> None:
        if name not in self.states:
            raise ValueError(f"No such state exists: '{name}'")
        
        self.selected_state = name
    
    def handle_events(self, event: pygame.Event) -> None:
        self._check_selected_state()
        ret = self.states[self.selected_state].handle_events(event)

        match ret:
            case self.settings.state.MAIN_MENU_KEY:
                self.set_state("main_menu")
            case self.settings.state.DANCE_SELECTION_KEY:
                self.set_state("dance_selection")

    def update(self, dt: float) -> None:
        self._check_selected_state()
        return self.states[self.selected_state].update(dt)

    def render(self, render_surface: pygame.Surface) -> None:
        self._check_selected_state()
        self.states[self.selected_state].render(render_surface)

