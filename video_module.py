import cv2
from numpy import ndarray
from typing import Union

class Video_Capture_Handler:
    def __init__(self, source=0) -> None:
        self.cap = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise ValueError(f"Error: Could not open video source {source}")
        
        self.is_live_stream = isinstance(source, int)

    def is_opened(self):
        return self.cap.isOpened()

    def read_frame(self):
        return self.cap.read()

    def release(self):
        self.cap.release()
    
    def get_framerate(self) -> Union[float, None]:
        if not self.cap: return
        return self.cap.get(cv2.CAP_PROP_FPS)
    
    def get_frame_size(self) -> Union[tuple, None]:
        if not self.cap: return
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    def set_position_msec(self, timestamp_ms: float) -> None:
        if self.is_live_stream:
            print("Warning: Seeking is not supported for live streams.")
            return False
        if not self.cap:
            return False
        return self.cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)

class Video_Recorder:
    def __init__(self, filename: str, fps: float, frame_size: tuple, codec: str = "mp4v") -> None:
        self.filename = filename
        self.fps = fps
        self.frame_size = frame_size
        self.codec = codec
        self.writer = None
    
    def start_recording(self) -> None:
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        self.writer = cv2.VideoWriter(
            filename=self.filename,
            fourcc=fourcc,
            fps=self.fps,
            frameSize=self.frame_size
        )

    def write_frame(self, frame: ndarray) -> None:
        if not self.writer: return
        self.writer.write(frame)

    def stop_recording(self) -> None:
        if not self.writer: return
        self.writer.release()
        self.writer = None