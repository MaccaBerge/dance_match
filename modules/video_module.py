import cv2
from numpy import ndarray
from typing import Union, Optional, Tuple

class Video_Capture_Handler:
    def __init__(self, source: Union[int, str] = 0) -> None:
        """
        Initializes the video capture handler.

        Args:
            source (Union[int, str]): The source of the video feed. It can be an integer representing a camera index
                                      or a string representing a file path.
        """
        self.cap: cv2.VideoCapture = cv2.VideoCapture(source)

        if not self.cap.isOpened():
            raise ValueError(f"Error: Could not open video source {source}")
        
        self.is_live_stream: bool = isinstance(source, int)

    def is_opened(self) -> bool:
        """
        Check if the video capture is successfully opened.

        Returns:
            bool: True if the capture is opened, otherwise False.
        """
        return self.cap.isOpened()

    def read_frame(self) -> Tuple[bool, Optional[ndarray]]:
        """
        Reads a frame from the video source.

        Returns:
            Tuple[bool, Optional[ndarray]]: A tuple where the first value is a boolean indicating success,
                                              and the second value is the frame (if read successfully).
        """
        return self.cap.read()

    def release(self) -> None:
        """
        Releases the video capture object.
        """
        self.cap.release()
    
    def get_framerate(self) -> Union[float, None]:
        """
        Get the framerate of the video.

        Returns:
            Union[float, None]: The framerate of the video or None if not available.
        """
        if not self.cap: 
            return None
        return self.cap.get(cv2.CAP_PROP_FPS)
    
    def get_number_of_frames(self) -> Union[int, None]:
        """
        Get the total number of frames in the video.

        Returns:
            Union[int, None]: The number of frames or None if it is a live stream.
        """
        if self.is_live_stream: 
            return None
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    def get_frame_size(self) -> Union[Tuple[int, int], None]:
        """
        Get the size of the frames.

        Returns:
            Union[Tuple[int, int], None]: The width and height of the frame as a tuple or None if not available.
        """
        if not self.cap: 
            return None
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    def set_position_msec(self, timestamp_ms: float) -> bool:
        """
        Sets the position of the video to a specific timestamp in milliseconds.

        Args:
            timestamp_ms (float): The timestamp in milliseconds to seek to.

        Returns:
            bool: True if the seek was successful, otherwise False.
        """
        if self.is_live_stream:
            print("Warning: Seeking is not supported for live streams.")
            return False
        if not self.cap:
            return False
        return self.cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
    
    def set_frame(self, frame_number: int) -> None:
        """
        Sets the current frame to a specific frame number.

        Args:
            frame_number (int): The frame number to seek to.
        """
        if self.is_live_stream: 
            return
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

class Video_Recorder:
    def __init__(self, filename: str, fps: float, frame_size: Tuple[int, int], codec: str = "mp4v") -> None:
        """
        Initializes the video recorder.

        Args:
            filename (str): The name of the output file.
            fps (float): The frames per second to use for the video.
            frame_size (Tuple[int, int]): The size of the video frames as (width, height).
            codec (str, optional): The codec to use for video encoding. Default is "mp4v".
        """
        self.filename: str = filename
        self.fps: float = fps
        self.frame_size: Tuple[int, int] = frame_size
        self.codec: str = codec
        self.writer: Optional[cv2.VideoWriter] = None
    
    def start_recording(self) -> None:
        """
        Starts the video recording.
        """
        fourcc: int = cv2.VideoWriter_fourcc(*self.codec)
        self.writer = cv2.VideoWriter(
            filename=self.filename,
            fourcc=fourcc,
            fps=self.fps,
            frameSize=self.frame_size
        )

    def write_frame(self, frame: ndarray) -> None:
        """
        Writes a frame to the video file.

        Args:
            frame (ndarray): The frame to write to the video.
        """
        if not self.writer: 
            return
        self.writer.write(frame)

    def stop_recording(self) -> None:
        """
        Stops the video recording and releases the video writer.
        """
        if not self.writer: 
            return
        self.writer.release()
        self.writer = None
