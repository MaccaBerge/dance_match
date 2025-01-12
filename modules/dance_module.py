import pygame
import os
from typing import List, Literal

from .pose_module import Pose_Sequence
from .video_module import Video_Capture_Handler
from .settings_module import Settings

class Dance:
    def __init__(self, name: str, video: Video_Capture_Handler, pose_sequence: Pose_Sequence, thumbnail: pygame.Surface) -> None:
        self.name = name
        self.video = video
        self.pose_sequence = pose_sequence
        self.thumbnail = thumbnail

        self.stars = 0
    
    def set_stars(self, number_of_starts: Literal[0, 1, 2, 3]) -> None:
        if number_of_starts not in (0,1,2,3): return
        self.stars = number_of_starts
    
    def get_name(self) -> str:
        return self.name
    
    def get_video(self) -> Video_Capture_Handler:
        return self.video
    
    def get_pose_sequence(self) -> Pose_Sequence:
        return self.pose_sequence
    
    def get_thumbnail(self) -> pygame.Surface:
        return self.thumbnail

class Dance_Loader:
    def __init__(self, settings: Settings):
        self.settings = settings

    def load_dance_data(self) -> List[Dance]:
        # Store all dances in list
        dances = []

        # Iterate through all directories in the dance folder
        for root, dirs, _ in os.walk(self.settings.path.DANCE_FOLDER_PATH):
            for folder_name in dirs:
                folder_path = os.path.join(root, folder_name)
                dance_data = self.process_folder(folder_path)
                dance = Dance(folder_name, dance_data["video"], dance_data["pose_sequence"], dance_data["thumbnail"])
                dances.append(dance)

        return dances

    def process_folder(self, folder_path):
        # Initialize default data as None
        data = {
            "video": None,
            "pose_sequence": None,
            "thumbnail": None,
        }

        files = os.listdir(folder_path)

        for file in files:
            file_path = os.path.join(folder_path, file)

            # Only process files
            if not os.path.isfile(file_path):
                continue

            # Match file prefixes and load the corresponding data
            if file.startswith(self.settings.dance.CLEAN_VIDEO_FILENAME):
                data["video"] = self.load_video(file_path)
            elif file.startswith(self.settings.dance.POSE_SEQUENCE_FILENAME):
                data["pose_sequence"] = self.load_pose_sequence(file_path)
            elif file.startswith(self.settings.dance.THUMBNAIL_FILENAME):
                data["thumbnail"] = self.load_thumbnail(file_path)
        
        if data["thumbnail"] is None:
            data["thumbnail"] = self.load_thumbnail("default_thumbnail.jpeg")

        return data

    def load_video(self, file_path):
        # Example of video loading
        video = Video_Capture_Handler(file_path)
        print(f"Loaded video from {file_path}")
        return video

    def load_pose_sequence(self, file_path):
        # Example of pose sequence loading
        pose_sequence = Pose_Sequence.load_from_json_file(file_path)
        print(f"Loaded pose sequence from {file_path}")
        return pose_sequence

    def load_thumbnail(self, file_path):
        # Example of thumbnail loading
        thumbnail = pygame.image.load(file_path).convert_alpha()
        thumbnail = pygame.transform.scale(
            thumbnail,
            (
                self.settings.button.DANCE_SELECT_BUTTON_WIDTH,
                self.settings.button.DANCE_SELECT_BUTTON_HEIGHT,
            ),
        )
        print(f"Loaded thumbnail from {file_path}")
        return thumbnail

    