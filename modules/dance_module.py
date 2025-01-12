import pygame
import os
from typing import List, Literal, Dict, Optional

from .pose_module import Pose_Sequence
from .video_module import Video_Capture_Handler
from .settings_module import Settings

class Dance:
    """
    Represents a dance with associated video, pose sequence, thumbnail, and star rating.
    """

    def __init__(self, name: str, video: Video_Capture_Handler, pose_sequence: Pose_Sequence, thumbnail: pygame.Surface) -> None:
        """
        Initializes a Dance object.

        Args:
            name (str): The name of the dance.
            video (Video_Capture_Handler): The video associated with the dance.
            pose_sequence (Pose_Sequence): The pose sequence data.
            thumbnail (pygame.Surface): The thumbnail image for the dance.
        """
        self.name: str = name
        self.video: Video_Capture_Handler = video
        self.pose_sequence: Pose_Sequence = pose_sequence
        self.thumbnail: pygame.Surface = thumbnail
        self.stars: int = 0  # Star rating of the dance (0-3).

    def set_stars(self, number_of_starts: Literal[0, 1, 2, 3]) -> None:
        """
        Sets the star rating for the dance.

        Args:
            number_of_starts (Literal[0, 1, 2, 3]): The number of stars to set (0-3).
        """
        if number_of_starts in (0, 1, 2, 3):
            self.stars = number_of_starts

    def get_name(self) -> str:
        """
        Returns the name of the dance.

        Returns:
            str: The name of the dance.
        """
        return self.name

    def get_video(self) -> Video_Capture_Handler:
        """
        Returns the video associated with the dance.

        Returns:
            Video_Capture_Handler: The video object.
        """
        return self.video

    def get_pose_sequence(self) -> Pose_Sequence:
        """
        Returns the pose sequence associated with the dance.

        Returns:
            Pose_Sequence: The pose sequence object.
        """
        return self.pose_sequence

    def get_thumbnail(self) -> pygame.Surface:
        """
        Returns the thumbnail image of the dance.

        Returns:
            pygame.Surface: The thumbnail surface.
        """
        return self.thumbnail


class Dance_Loader:
    """
    Handles the loading of dance data from directories.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initializes a Dance_Loader object.

        Args:
            settings (Settings): The settings object containing configuration paths.
        """
        self.settings: Settings = settings

    def load_dance_data(self) -> List[Dance]:
        """
        Loads all dance data from the configured directory.

        Returns:
            List[Dance]: A list of Dance objects.
        """
        dances: List[Dance] = []

        # Iterate through all directories in the dance folder
        for root, dirs, _ in os.walk(self.settings.path.DANCE_FOLDER_PATH):
            for folder_name in dirs:
                folder_path = os.path.join(root, folder_name)
                dance_data = self.process_folder(folder_path)
                dance = Dance(folder_name, dance_data["video"], dance_data["pose_sequence"], dance_data["thumbnail"])
                dances.append(dance)

        return dances

    def process_folder(self, folder_path: str) -> Dict[str, Optional[object]]:
        """
        Processes a folder to extract dance data (video, pose sequence, thumbnail).

        Args:
            folder_path (str): The path to the folder.

        Returns:
            Dict[str, Optional[object]]: A dictionary containing video, pose_sequence, and thumbnail data.
        """
        data: Dict[str, Optional[object]] = {
            "video": None,
            "pose_sequence": None,
            "thumbnail": None,
        }

        files: List[str] = os.listdir(folder_path)

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

        # Use a default thumbnail if none is provided
        if data["thumbnail"] is None:
            data["thumbnail"] = self.load_thumbnail("default_thumbnail.jpeg")

        return data

    def load_video(self, file_path: str) -> Video_Capture_Handler:
        """
        Loads a video file.

        Args:
            file_path (str): The path to the video file.

        Returns:
            Video_Capture_Handler: The loaded video object.
        """
        video = Video_Capture_Handler(file_path)
        print(f"Loaded video from {file_path}")
        return video

    def load_pose_sequence(self, file_path: str) -> Pose_Sequence:
        """
        Loads a pose sequence file.

        Args:
            file_path (str): The path to the pose sequence file.

        Returns:
            Pose_Sequence: The loaded pose sequence object.
        """
        pose_sequence = Pose_Sequence.load_from_json_file(file_path)
        print(f"Loaded pose sequence from {file_path}")
        return pose_sequence

    def load_thumbnail(self, file_path: str) -> pygame.Surface:
        """
        Loads a thumbnail image and scales it to the appropriate size.

        Args:
            file_path (str): The path to the thumbnail file.

        Returns:
            pygame.Surface: The loaded and scaled thumbnail surface.
        """
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
