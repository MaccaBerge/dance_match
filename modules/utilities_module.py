import cv2
import pygame
from typing import Optional

from .pose_module import Pose_Sequence, Pose_Landmarker_Model, Pose_Visualizer
from .video_module import Video_Capture_Handler, Video_Recorder

def annotate_pose_sequence_to_video(video_obj: Video_Capture_Handler, pose_sequence: Pose_Sequence, save_path: str = "annotated_video.mp4") -> None:
    """
    Annotates a pose sequence onto a video by overlaying the detected pose landmarks at corresponding times.

    Args:
        video_obj (Video_Capture_Handler): The object responsible for video capture.
        pose_sequence (Pose_Sequence): The sequence of poses to overlay on the video.
        save_path (str, optional): The path where the annotated video will be saved. Default is "annotated_video.mp4".

    Raises:
        ValueError: If the provided `video_obj` is not an instance of `Video_Capture_Handler` or `pose_sequence` is not an instance of `Pose_Sequence`.
    """
    if not isinstance(video_obj, Video_Capture_Handler):
        raise ValueError(f"Invalid type for 'video_obj': expected 'Video_Capture_Handler', got {type(video_obj).__name__}")
    if not isinstance(pose_sequence, Pose_Sequence):
        raise ValueError(f"Invalid type for 'pose_sequence': expected 'Pose_Sequence', got {type(pose_sequence).__name__}")
    
    video_recorder: Video_Recorder = Video_Recorder(save_path, video_obj.get_framerate(), video_obj.get_frame_size())
    video_recorder.start_recording()

    pose_landmarker_model: Pose_Landmarker_Model = Pose_Landmarker_Model("models/pose_landmarker_full.task")
    pose_landmarker_model.initialize()

    running: bool = True

    while running:
        ret, frame = video_obj.read_frame()

        if not ret:
            print("No Returned Value")
            break

        timestamp_ms: int = int(video_obj.cap.get(cv2.CAP_PROP_POS_MSEC))
        closest_pose: Optional[Pose_Sequence] = pose_sequence.get_closest_pose_at(timestamp_ms)

        rgb_frame: pygame.Surface = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_annotated_frame: pygame.Surface = Pose_Visualizer.draw_landmarks(rgb_frame, closest_pose)

        bgr_annotated_frame: pygame.Surface = cv2.cvtColor(rgb_annotated_frame, cv2.COLOR_RGB2BGR)

        video_recorder.write_frame(bgr_annotated_frame)

        print("Frame: ", video_obj.cap.get(cv2.CAP_PROP_POS_FRAMES), "Time: ", video_obj.cap.get(cv2.CAP_PROP_POS_MSEC))
    
    video_recorder.stop_recording()

def apply_tint(image: pygame.Surface, color: tuple[int, int, int], intensity: int) -> pygame.Surface:
    """
    Apply a color tint to a Pygame image.

    Args:
        image (pygame.Surface): The original image to apply the tint to.
        color (tuple[int, int, int]): A tuple of RGB values for the tint color (e.g., (255, 255, 255) for white).
        intensity (int): The intensity of the tint (0 to 255), where 0 is no tint and 255 is full tint.

    Returns:
        pygame.Surface: A new surface with the tint applied.
    """
    tinted_image: pygame.Surface = image.copy()
    tint: pygame.Surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    tint.fill((color[0], color[1], color[2], intensity))

    tinted_image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    return tinted_image
