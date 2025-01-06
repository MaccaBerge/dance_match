

class Display_Settings:
    WIDTH: int = 1200
    HEIGHT: int = 750
    FPS: float = 60.0

class State_Settings:
    MAIN_MENU_KEY: str = "main_menu"
    DANCE_SELECTION_KEY: str = "dance_selection"


class Settings:
    display: Display_Settings = Display_Settings()
    state: State_Settings = State_Settings()

