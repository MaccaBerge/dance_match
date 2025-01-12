import cv2
import pygame

from .pose_module import Pose_Sequence, Pose_Landmarker_Model, Pose_Visualizer
from .video_module import Video_Capture_Handler, Video_Recorder


def annotate_pose_sequence_to_video(video_obj: Video_Capture_Handler, pose_sequence: Pose_Sequence, save_path: str = "annotated_video.mp4") -> None:
    if not isinstance(video_obj, Video_Capture_Handler):
        raise ValueError(f"Invalid type for 'video_obj': expected 'Video_Capture_Handler', got {type(video_obj).__name__}")
    if not isinstance(pose_sequence, Pose_Sequence):
        raise ValueError(f"Invalid type for 'pose_sequence': expected 'Pose_Sequence', got {type(pose_sequence).__name__}")
    

    video_recorder = Video_Recorder(save_path, video_obj.get_framerate(), video_obj.get_frame_size())
    video_recorder.start_recording()

    pose_landmarker_model = Pose_Landmarker_Model("models/pose_landmarker_full.task")
    pose_landmarker_model.initialize()

    running = True

    while running:
        ret, frame = video_obj.read_frame()

        if not ret:
            print("No Returned Value")
            break

        timestamp_ms = int(video_obj.cap.get(cv2.CAP_PROP_POS_MSEC))

        closest_pose = pose_sequence.get_closest_pose_at(timestamp_ms)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_annotated_frame = Pose_Visualizer.draw_landmarks(rgb_frame, closest_pose)

        bgr_annotated_frame = cv2.cvtColor(rgb_annotated_frame, cv2.COLOR_RGB2BGR)

        video_recorder.write_frame(bgr_annotated_frame)


        print("Frame: ", video_obj.cap.get(cv2.CAP_PROP_POS_FRAMES), "Time: ", video_obj.cap.get(cv2.CAP_PROP_POS_MSEC))
    
    video_recorder.stop_recording()


def apply_tint(image: pygame.Surface, color: tuple[int, int, int], intensity: int) -> pygame.Surface:
    """
    Apply a color tint to a Pygame image.

    Args:
        image (pygame.Surface): The original image.
        color (tuple): RGB values of the tint color (e.g., (255, 255, 255) for white).
        intensity (int): The tint intensity (0 to 255).

    Returns:
        pygame.Surface: A new tinted image.
    """
    # Create a copy of the original image
    tinted_image = image.copy()
    
    # Create a surface filled with the tint color
    tint = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    tint.fill((color[0], color[1], color[2], intensity))  # Add the alpha for transparency

    # Blit the tint onto the original image
    tinted_image.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return tinted_image