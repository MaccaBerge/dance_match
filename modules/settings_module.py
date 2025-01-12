import pygame
from os.path import abspath

class Display_Settings:
    WIDTH: int = 1200
    HEIGHT: int = 750
    FPS: float = 60.0

class State_Settings:
    STATE_MAIN_MENU_KEY: str = "STATE_MAIN_MENU"
    STATE_DANCE_SELECTION_KEY: str = "STATE_DANCE_SELECTION"
    STATE_PLAY_DANCE_KEY: str = "STATE_PLAY_DANCE"
    STATE_SCOREBOARD_KEY: str = "STATE_SCOREBOARD"

    PLAY_DANCE_KEY: str = "PLAY_DANCE."
    PLAY_DANCE_KEY_SPLIT_CHARACTHER: str = "."

    DANCE_SCORE_KEY: str = "DANCE_SCORE."
    DANCE_SCORE_KEY_SPLIT_CHARACTHER: str = "."

    QUIT_KEY: str = "QUIT"

class Button_Settings:
    NORMAL_COLOR: pygame.Color = pygame.Color("#E0E0E0")
    HOVER_COLOR: pygame.Color = pygame.Color("#BDBDBD")
    PRESSED_COLOR: pygame.Color = pygame.Color("#757575")

    IMAGE_HOVER_TINT_COLOR: pygame.Color = pygame.Color(100,0,0)
    IMAGE_PRESSED_TINT_COLOR: pygame.Color = pygame.Color(0,0,100)

    IMAGE_HOVER_TINT_INTENSITY: int = 200
    IMAGE_PRESSED_TINT_INTENSITY: int = 200

    DANCE_SELECT_BUTTON_WIDTH: int = 200
    DANCE_SELECT_BUTTON_HEIGHT: int = 150

class Path_Settings:
    DANCE_FOLDER_PATH: abspath = abspath("dances")
    BLOCKY_FONT_PATH: abspath = abspath("fonts/Akira Expanded Demo.otf")
    LANDMARK_MODEL_PATH: abspath = abspath("models/pose_landmarker_full.task")

class Dance_Settings:
    CLEAN_VIDEO_FILENAME: str = "clean_dance_video"
    ANNOTATED_VIDEO_FILENAME: str = "annotated_dance_video"
    POSE_SEQUENCE_FILENAME: str = "pose_sequence_data"
    THUMBNAIL_FILENAME: str = "thumbnail"

class Camera_Settings:
    CAMERA_INDEX: int = 0

class Settings:
    display: Display_Settings = Display_Settings()
    state: State_Settings = State_Settings()
    button: Button_Settings = Button_Settings()
    path: Path_Settings = Path_Settings()
    dance: Dance_Settings = Dance_Settings()
    camera: Camera_Settings = Camera_Settings()

