import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
from numpy import copy
from os.path import exists
from typing import Union
import json
import numpy as np

class Pose:
    def __init__(self, landmarks, timestamp_ms) -> None:
        self.landmarks = landmarks
        self.timestamp_ms = timestamp_ms
    
    def to_dict(self) -> dict:
        return {
            "timestamp_ms": self.timestamp_ms,
            "landmarks": [
                [{"x": round(lm.x, 3), "y": round(lm.y, 3), "z": round(lm.z, 3), "visibility": round(lm.visibility, 3), 
                "presence": round(lm.presence, 3)} for lm in pose] for pose in self.landmarks
                ]
        }
    
    @staticmethod
    def from_dict(pose_dict: dict) -> "Pose":
        if not isinstance(pose_dict, dict):
            raise ValueError("Expected dictionary")
        
        landmarks = [
            [landmark_pb2.NormalizedLandmark(
                x=lm["x"], y=lm["y"], z=lm["z"], 
                visibility=lm["visibility"], presence=lm["presence"]) 
                for lm in pose] for pose in pose_dict["landmarks"]
        ]
        
        return Pose(landmarks=landmarks, timestamp_ms=pose_dict["timestamp_ms"])
        
class Pose_Sequence:
    def __init__(self, time_between_poses_ms: int) -> None:
        self.time_between_poses_ms = time_between_poses_ms
        self.poses = []
    
    def add_pose(self, pose: Pose) -> None:
        if not isinstance(pose, Pose):
            raise TypeError("Expected Pose object")
        self.poses.append(pose)
    
    def get_closest_pose_at(self, timestamp_ms: int) -> Pose:
        closest_pose = min(self.poses, key=lambda pose: abs(pose.timestamp_ms - timestamp_ms))
        return closest_pose

    def to_dict(self) -> dict:
        return {
            "time_between_poses_ms": self.time_between_poses_ms,
            "poses": [pose.to_dict() for pose in self.poses]
        }
    
    def save_to_json_file(self, path: str) -> None:
        try:
            with open(path, "w") as file:
                json.dump(self.to_dict(), file, indent=4)
        except Exception as e:
            print(f"Error saving to {path}: {e}")
            
    @staticmethod
    def load_from_json_file(path: str) -> Union["Pose_Sequence", None]:
        if not exists(path):
            raise FileNotFoundError(f"File Not Found: {path}")
        
        try:
            with open(path, "r") as file:
                data = json.load(file)
            
            time_between_poses_ms = data["time_between_poses_ms"]
            
            pose_sequence = Pose_Sequence(time_between_poses_ms)
            for pose_dict in data["poses"]:
                pose = Pose.from_dict(pose_dict)
                pose_sequence.add_pose(pose)

            return pose_sequence

        except Exception as e:
            print(f"Error loading from {path}: {e}")

class Pose_Landmarker_Model:
    def __init__(self, model_path: str) -> None:
        self.latest_result = None
        self.latest_image = None
        self.model_path = model_path
        self.landmarker = None

    def initialize(self):
        base_options = mp.tasks.BaseOptions
        pose_landmarker = mp.tasks.vision.PoseLandmarker
        pose_landmarker_options = mp.tasks.vision.PoseLandmarkerOptions
        vision_running_mode = mp.tasks.vision.RunningMode

        options = pose_landmarker_options(
            base_options=base_options(model_asset_path=self.model_path),
            running_mode=vision_running_mode.LIVE_STREAM,
            result_callback=self._result_callback
        )
        self.landmarker = pose_landmarker.create_from_options(options)

    def _result_callback(self, result, output_image, timestamp_ms):
        self.latest_result = result
        self.latest_image = output_image

    def process_frame(self, frame, timestamp_ms):
        if self.landmarker:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            self.landmarker.detect_async(mp_image, timestamp_ms)

    def get_latest_result(self):
        return self.latest_result
    
    def get_latest_frame(self) -> mp.Image:
        return self.latest_image

class Pose_Visualizer:
    @staticmethod
    def draw_landmarks(rgb_image: np.ndarray, pose: Pose) -> np.ndarray:
        if not isinstance(pose, Pose): 
            raise TypeError("Expected Pose object")
        if not pose.landmarks: return rgb_image

        pose_landmarks_list = pose.landmarks.copy()
        annotated_image = copy(rgb_image)

        # Loop through detected poses and visualize landmarks
        for idx in range(len(pose_landmarks_list)):
            pose_landmarks = pose_landmarks_list[idx]
            pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(
                    x=landmark.x, y=landmark.y, z=landmark.z
                ) for landmark in pose_landmarks
            ])
            mp.solutions.drawing_utils.draw_landmarks(
                annotated_image,
                pose_landmarks_proto,
                mp.solutions.pose.POSE_CONNECTIONS,
                mp.solutions.drawing_styles.get_default_pose_landmarks_style()
            )
        return annotated_image

