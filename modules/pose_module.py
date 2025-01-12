import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
from numpy import copy, ndarray
import fastdtw
from scipy.spatial.distance import cosine
from os.path import exists
import json
from typing import Union

def compare_poses(pose1: "Pose", pose2: "Pose") -> float:
    """
    Compares two poses and calculates the distance between them using Dynamic Time Warping (DTW) 
    with cosine distance as the metric.
    
    Args:
        pose1 (Pose): The first pose object.
        pose2 (Pose): The second pose object.
    
    Returns:
        float: The DTW distance between the two poses, or None if an error occurs.
    """
    try:
        # Convert the landmarks of each pose to a list of [x, y, z] coordinates
        pose1 = [[lm.x, lm.y, lm.z] for lm in pose1.landmarks[0]]
        pose2 = [[lm.x, lm.y, lm.z] for lm in pose2.landmarks[0]]

        # Compute the DTW distance with cosine as the distance metric
        distance, _ = fastdtw.fastdtw(pose1, pose2, dist=cosine)
        return distance
    except:
        return None

class Pose:
    """
    A class representing a pose, which consists of a set of landmarks and a timestamp.
    """

    def __init__(self, landmarks, timestamp_ms) -> None:
        """
        Initializes a Pose object with landmarks and a timestamp.

        Args:
            landmarks (list): List of landmark objects representing the pose's landmarks.
            timestamp_ms (int): Timestamp of the pose in milliseconds.
        """
        self.landmarks = landmarks
        self.timestamp_ms = timestamp_ms
    
    def to_dict(self) -> dict:
        """
        Converts the Pose object to a dictionary representation.
        
        Returns:
            dict: A dictionary containing the pose's timestamp and landmarks.
        """
        return {
            "timestamp_ms": self.timestamp_ms,
            "landmarks": [
                [{"x": round(lm.x, 3), "y": round(lm.y, 3), "z": round(lm.z, 3), "visibility": round(lm.visibility, 3), 
                "presence": round(lm.presence, 3)} for lm in pose] for pose in self.landmarks
                ]
        }
    
    @staticmethod
    def from_dict(pose_dict: dict) -> "Pose":
        """
        Converts a dictionary to a Pose object.
        
        Args:
            pose_dict (dict): A dictionary representing a pose.
        
        Returns:
            Pose: The corresponding Pose object.
        
        Raises:
            ValueError: If the input is not a dictionary.
        """
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
    """
    A class to represent a sequence of poses. 
    It allows adding poses, retrieving the closest pose to a timestamp, 
    and saving or loading the sequence from a JSON file.
    """

    def __init__(self, time_between_poses_ms: int) -> None:
        """
        Initializes a Pose_Sequence object with the time interval between poses.
        
        Args:
            time_between_poses_ms (int): The time interval between consecutive poses in milliseconds.
        """
        self.time_between_poses_ms = time_between_poses_ms
        self.poses = []

    def add_pose(self, pose: Pose) -> None:
        """
        Adds a Pose object to the sequence.
        
        Args:
            pose (Pose): The pose object to be added.
        
        Raises:
            TypeError: If the input is not a Pose object.
        """
        if not isinstance(pose, Pose):
            raise TypeError("Expected Pose object")
        self.poses.append(pose)

    def get_closest_pose_at(self, timestamp_ms: int) -> Pose:
        """
        Retrieves the closest pose in the sequence to the specified timestamp.
        
        Args:
            timestamp_ms (int): The timestamp (in milliseconds) for which to find the closest pose.
        
        Returns:
            Pose: The closest Pose object to the given timestamp.
        """
        closest_pose = min(self.poses, key=lambda pose: abs(pose.timestamp_ms - timestamp_ms))
        return closest_pose

    def to_dict(self) -> dict:
        """
        Converts the Pose_Sequence object to a dictionary.
        
        Returns:
            dict: A dictionary representing the Pose_Sequence object.
        """
        return {
            "time_between_poses_ms": self.time_between_poses_ms,
            "poses": [pose.to_dict() for pose in self.poses]
        }
    
    def save_to_json_file(self, path: str) -> None:
        """
        Saves the Pose_Sequence object to a JSON file.
        
        Args:
            path (str): The file path to save the sequence.
        """
        try:
            with open(path, "w") as file:
                json.dump(self.to_dict(), file, indent=4)
        except Exception as e:
            print(f"Error saving to {path}: {e}")
            
    @staticmethod
    def load_from_json_file(path: str) -> Union["Pose_Sequence", None]:
        """
        Loads a Pose_Sequence object from a JSON file.
        
        Args:
            path (str): The file path to load the sequence from.
        
        Returns:
            Pose_Sequence: The loaded Pose_Sequence object, or None if an error occurs.
        
        Raises:
            FileNotFoundError: If the file does not exist.
        """
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
    """
    A class to interface with the MediaPipe PoseLandmarker model, which detects poses in video frames.
    """

    def __init__(self, model_path: str) -> None:
        """
        Initializes the PoseLandmarker model with the given model path.
        
        Args:
            model_path (str): The file path to the model asset.
        """
        self.latest_result = None
        self.latest_image = None
        self.model_path = model_path
        self.landmarker = None

    def initialize(self) -> None:
        """
        Initializes the PoseLandmarker model with options for real-time stream processing.
        """
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

    def _result_callback(self, result, output_image, timestamp_ms) -> None:
        """
        Callback function to store the result and image after processing a frame.
        
        Args:
            result: The result of pose detection.
            output_image: The image with landmarks drawn on it.
            timestamp_ms (int): The timestamp in milliseconds.
        """
        self.latest_result = result
        self.latest_image = output_image

    def process_frame(self, frame, timestamp_ms):
        """
        Processes a single frame to detect poses.
        
        Args:
            frame: The image frame to process.
            timestamp_ms (int): The timestamp in milliseconds.
        """
        if self.landmarker:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            self.landmarker.detect_async(mp_image, timestamp_ms)

    def get_latest_result(self):
        """
        Returns the latest pose detection result.
        
        Returns:
            The latest result from the pose landmarker.
        """
        return self.latest_result
    
    def get_latest_frame(self) -> mp.Image:
        """
        Returns the latest processed frame with drawn landmarks.
        
        Returns:
            mp.Image: The image with landmarks drawn.
        """
        return self.latest_image

class Pose_Visualizer:
    """
    A class to visualize poses by drawing landmarks on an image.
    """

    @staticmethod
    def draw_landmarks(rgb_image: ndarray, pose: Pose) -> ndarray:
        """
        Draws the landmarks of a Pose on an image.
        
        Args:
            rgb_image (ndarray): The RGB image to draw on.
            pose (Pose): The Pose object containing landmarks to draw.
        
        Returns:
            ndarray: The image with the drawn landmarks.
        
        Raises:
            TypeError: If the input is not a Pose object.
        """
        if not isinstance(pose, Pose): 
            raise TypeError("Expected Pose object")
        if not pose.landmarks: return rgb_image

        pose_landmarks_list = pose.landmarks.copy()
        annotated_image = copy(rgb_image)

        # Loop through detected poses and visualize landmarks
        for idx in range(len(pose_landmarks_list)):
            pose_landmarks = pose_landmarks_list[idx]
            pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend([landmark_pb2.NormalizedLandmark(
                    x=landmark.x, y=landmark.y, z=landmark.z
                ) for landmark in pose_landmarks])
            mp.solutions.drawing_utils.draw_landmarks(
                annotated_image,
                pose_landmarks_proto,
                mp.solutions.pose.POSE_CONNECTIONS,
                mp.solutions.drawing_styles.get_default_pose_landmarks_style()
            )
        return annotated_image
