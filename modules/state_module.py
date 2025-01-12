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
    """
    Manages different game states and transitions between them.
    It maintains a collection of game states and handles the switching between states.
    """
    def __init__(self, settings: Settings) -> None:
        """
        Initializes the Game_State_Manager with the given settings.
        
        Args:
            settings (Settings): The settings object containing game configurations.
        """
        self.settings: Settings = settings  # Stores the settings for the game
        self.states: Dict[str, Game_State] = {}  # A dictionary of game states, keyed by their names
        self.selected_state: Optional[Game_State] = None  # The currently selected game state, or None if no state is selected

    def _check_selected_state(self) -> None:
        """
        Verifies that a valid state is selected. Raises an error if no state is selected or if the selected state is invalid.
        
        Raises:
            RuntimeError: If no state is selected or if the selected state is not valid.
        """
        if not self.selected_state:
            raise RuntimeError("No state selected")
        
        if self.selected_state not in self.states:
            raise RuntimeError("The selected state is not a valid state")

    def add_state(self, name: str, state: Game_State) -> None:
        """
        Adds a new game state to the manager.
        
        Args:
            name (str): The name of the state. This should be a unique string.
            state (Game_State): An instance of a game state to add.
        
        Raises:
            ValueError: If the name is not a string or the state is not a subclass of Game_State.
        """
        # Validate the type of the name and state
        if not isinstance(name, str):
            raise ValueError(f"Invalid type for 'name': expected 'str', got {type(name).__name__}")
        if not issubclass(type(state), Game_State):
            raise ValueError(f"Invalid type for 'state': expected subclass of 'Game_State', got {type(state).__name__}")
        
        self.states[name] = state  # Add the state to the dictionary of states
    
    def set_state(self, name: str) -> None:
        """
        Sets the currently active game state to the one identified by the given name.
        
        Args:
            name (str): The name of the state to set as active.
        
        Raises:
            ValueError: If the state name does not exist in the states dictionary.
        """
        if name not in self.states:
            raise ValueError(f"No such state exists: '{name}'")
        
        self.selected_state = name  # Set the selected state
    
    def handle_events(self, event: pygame.Event) -> None:
        """
        Processes the events (e.g., user input) for the current state.
        
        Args:
            event (pygame.Event): A Pygame event to process.
        
        Raises:
            RuntimeError: If no valid state is selected.
        """
        self._check_selected_state()  # Ensure a valid state is selected
        self.states[self.selected_state].handle_events(event)  # Call the handle_events method of the current state

    def update(self, dt: float) -> None:
        """
        Updates the current game state logic.
        
        Args:
            dt (float): The time difference (delta time) since the last update, used for time-based updates.
        
        Raises:
            RuntimeError: If no valid state is selected.
        
        Returns:
            None
        """
        self._check_selected_state()  # Ensure a valid state is selected
        return self.states[self.selected_state].update(dt)  # Call the update method of the current state

    def render(self, render_surface: pygame.Surface) -> None:
        """
        Renders the current game state to the given surface.
        
        Args:
            render_surface (pygame.Surface): The surface to render to (typically the game screen).
        
        Raises:
            RuntimeError: If no valid state is selected.
        """
        self._check_selected_state()  # Ensure a valid state is selected
        self.states[self.selected_state].render(render_surface)  # Call the render method of the current state