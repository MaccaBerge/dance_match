class Game_State:
    """This serves as a base class for all game states."""
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
    def __init__(self) -> None:
        self.states = {}
        self.selected_state = None

    def add_state(self, name: str, state: Game_State) -> None:
        if not isinstance(name, str):
            raise ValueError(f"Invalid tpye for 'name': expected 'str', got {type(name).__name__}")
        if not issubclass(type(state), Game_State):
            raise ValueError(f"Invalid type for 'state': expected subclass of 'Game_State', got {type(state).__name__}")
        
        self.states[name] = state
    
    def set_state(self, name: str) -> None:
        pass

