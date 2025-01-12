import pygame
from os.path import abspath

class Display_Settings:
    WIDTH: int = 1200
    HEIGHT: int = 750
    FPS: float = 60.0

class State_Settings:
    MAIN_MENU_KEY: str = "MAIN_MENU"
    DANCE_SELECTION_KEY: str = "DANCE_SELECTION"
    QUIT_KEY: str = "QUIT"

class Button_Settings:
    NORMAL_COLOR: pygame.Color = pygame.Color("#E0E0E0")
    HOVER_COLOR: pygame.Color = pygame.Color("#BDBDBD")
    PRESSED_COLOR: pygame.Color = pygame.Color("#757575")

    DANCE_SELECT_BUTTON_WIDTH: int = 200
    DANCE_SELECT_BUTTON_HEIGHT: int = 150

class Path_Settings:
    DANCE_FOLDER_PATH: abspath = abspath("dances")

class Dance_Settings:
    CLEAN_VIDEO_FILENAME: str = "clean_dance_video"
    ANNOTATED_VIDEO_FILENAME: str = "annotated_dance_video"
    POSE_SEQUENCE_FILENAME: str = "pose_sequence_data"
    THUMBNAIL_FILENAME: str = "thumbnail"

class Settings:
    display: Display_Settings = Display_Settings()
    state: State_Settings = State_Settings()
    button: Button_Settings = Button_Settings()
    path: Path_Settings = Path_Settings()
    dance: Dance_Settings = Dance_Settings()

