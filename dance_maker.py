import cv2
from os import makedirs
from os.path import exists, join
from typing import Any, Union

from modules.pose_module import Pose, Pose_Sequence, Pose_Landmarker_Model, Pose_Visualizer
from modules.video_module import Video_Capture_Handler, Video_Recorder
from modules.timer_module import Timer_Thread
from modules.utils import annotate_pose_sequence_to_video

class Dance_Maker:
    def __init__(self, pose_model_path: str, storage_base_path: str = "./", clean_video_filename: str = "clean_dance_video.mp4",
                 annotated_video_filename: str = "annotated_dance_video.mp4", 
                 pose_sequence_data_filename: str = "pose_sequence_data.json") -> None:
        self.pose_landmark_model = Pose_Landmarker_Model(pose_model_path)
        self.storage_base_path = storage_base_path
        self.clean_video_name = clean_video_filename
        self.annotated_video_name = annotated_video_filename
        self.pose_sequence_data_filename = pose_sequence_data_filename
        self.output_folder_path = None
        self.video_handler = None
        self.clean_video_recorder = None
        self.annotated_video_recorder = None
        self.interval_timer = None
        self.pose_sequence = None
        self.latest_rgb_frame = None
        self.latest_pose = None
    
    def _initialize_output_folder(self, name: str) -> str:
        if not exists(self.storage_base_path):
            raise ValueError(f"The specified path does not exist: {self.storage_base_path}")

        unique_folder_name = name
        counter = 2
        folder_path = join(self.storage_base_path, unique_folder_name)

        while exists(folder_path):
            unique_folder_name = f"{name}_{counter}"
            folder_path = join(self.storage_base_path, unique_folder_name)
            counter += 1
        
        try:
            makedirs(folder_path)
        except Exception as e:
            raise OSError(f"Failed to create folder '{folder_path}'. Error: {e}")
        
        return folder_path
    
    def _initialize_video_resources(self, dance_name: str, source: Union[int, str], time_between_poses_ms: int) -> None:
        try:
            self.video_handler = Video_Capture_Handler(source=source)
        
            self.output_folder_path = self._initialize_output_folder(dance_name)

            self.pose_sequence = Pose_Sequence(time_between_poses_ms=time_between_poses_ms)
            self.pose_landmark_model.initialize()

            return True
        except Exception as e:
            print(f"Could not acces the video. Error: {e}")
            return False

    def _initialize_webcam_resources(self, dance_name: str, source: Union[int, str]) -> None:
        try:
            self.video_handler = Video_Capture_Handler(source=source)
        except Exception as e:
            print(f"Could not access the webcam. Error: {e}")
            return False
        
        self.output_folder_path = self._initialize_output_folder(dance_name)

        self.annotated_video_recorder = Video_Recorder(
            filename=join(self.output_folder_path, self.annotated_video_name),
            fps=self.video_handler.get_framerate() or 30, 
            frame_size=self.video_handler.get_frame_size() or (640, 480))
        
        self.clean_video_recorder = Video_Recorder(
            filename=join(self.output_folder_path, self.clean_video_name),
            fps=self.video_handler.get_framerate() or 30, 
            frame_size=self.video_handler.get_frame_size() or (640, 480))
        
        self.interval_timer = Timer_Thread(50, self._webcam_timer_callback)
        self.pose_sequence = Pose_Sequence(int(self.interval_timer.time_interval_ms))
        self.pose_landmark_model.initialize()
        return True
    
    def _cleanup_webcam_resources(self) -> None:
        if self.clean_video_recorder: self.clean_video_recorder.stop_recording()
        if self.annotated_video_recorder: self.annotated_video_recorder.stop_recording()
        if self.video_handler: self.video_handler.release()
        if self.interval_timer:
            self.interval_timer.stop()
            self.interval_timer.join()
        cv2.destroyAllWindows()
    
    def _cleanup_video_resources(self) -> None:
        if self.video_handler: self.video_handler.release()
        cv2.destroyAllWindows()
    
    def _webcam_timer_callback(self, data: Any) -> None:
        if self.latest_rgb_frame is None: return

        timestamp_ms = int(data["passed_time_ms"])
        self.pose_landmark_model.process_frame(self.latest_rgb_frame, timestamp_ms)

        result = self.pose_landmark_model.get_latest_result()
        if result is None: return
        
        self.latest_pose = Pose(result.pose_landmarks, timestamp_ms)
        self.pose_sequence.add_pose(self.latest_pose)

    def make_from_webcam(self, dance_name: str, camera_index: int = 0) -> None:
        try:
            if not self._initialize_webcam_resources(dance_name, camera_index):
                return
            
            self.clean_video_recorder.start_recording()
            self.annotated_video_recorder.start_recording()
            self.interval_timer.start() 
            running = True

            while running:
                ret, frame = self.video_handler.read_frame()
                
                if not ret:
                    print("Error: Unable to capture video.")
                    continue

                self.latest_rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                if self.latest_pose:
                    annotated_rgb_frame = Pose_Visualizer.draw_landmarks(self.latest_rgb_frame.copy(), self.latest_pose)
                    self.latest_rgb_frame = annotated_rgb_frame

                bgr_frame = cv2.cvtColor(self.latest_rgb_frame, cv2.COLOR_RGB2BGR)

                self.clean_video_recorder.write_frame(frame)
                self.annotated_video_recorder.write_frame(bgr_frame)
                
                cv2.imshow("Dance Maker 'Cam-Mode'", bgr_frame)

                if cv2.waitKey(1) == ord("q"):
                    running = False

        except Exception as e:
            print(f"Error: {e}")

        finally:
            self._cleanup_webcam_resources()
            if self.pose_sequence: self.pose_sequence.save_to_json_file(join(self.output_folder_path, self.pose_sequence_data_filename))

    def make_from_video(self, video_path: str, dance_name: str, time_between_poses_ms) -> None:
        try:
            if not self._initialize_video_resources(dance_name, video_path, time_between_poses_ms):
                print("Couldnt inizialize video_resources.")
                return
            
            number_of_frames = self.video_handler.get_number_of_frames()
            fps = self.video_handler.get_framerate()
            duration_ms = int(number_of_frames / fps * 1000)
            
            timestamp_ms = 0
            
            running = True
            while running:
                print(f"Proccessing frame at {timestamp_ms}/{duration_ms}ms")
                self.video_handler.set_position_msec(timestamp_ms)
                ret, frame = self.video_handler.read_frame()
                if not ret: return

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                self.pose_landmark_model.process_frame(rgb_frame, timestamp_ms)
                result = self.pose_landmark_model.get_latest_result()
                timestamp_ms += time_between_poses_ms
                if result is None: continue

                self.pose_sequence.add_pose(Pose(result.pose_landmarks, timestamp_ms))

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.video_handler.set_frame(0)
            annotate_pose_sequence_to_video(self.video_handler, self.pose_sequence, save_path=join(self.output_folder_path, self.annotated_video_name))
            self._cleanup_video_resources()
            if self.pose_sequence: self.pose_sequence.save_to_json_file(join(self.output_folder_path, self.pose_sequence_data_filename))


if __name__ == "__main__":
    dance_maker = Dance_Maker("models/pose_landmarker_full.task", storage_base_path="dances")
    dance_maker.make_from_webcam("Dance_Test")
    #dance_maker.make_from_video(video_path="test_dance.mov", dance_name="video_test", time_between_poses_ms=50)