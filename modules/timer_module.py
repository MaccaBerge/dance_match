import time
import threading
from typing import Callable, Any

class Timer_Thread(threading.Thread):
    """
    A thread-based timer that triggers a callback function at regular intervals.
    This class runs in its own thread, calling the provided callback function
    every `time_interval_ms` milliseconds. The timer continues running until
    explicitly stopped.

    Attributes:
        time_interval_ms (float): The time interval in milliseconds between each callback.
        callback (Callable[[float], Any]): The function to call when the interval is reached.
        passed_time (float): The amount of time in milliseconds that has passed since the start.
        running (bool): A flag indicating whether the timer is still running or has been stopped.
    """
    def __init__(self, time_interval_ms: float, callback: Callable[[float], Any]) -> None:
        """
        Initializes the Timer_Thread with a time interval and a callback function.

        Args:
            time_interval_ms (float): The interval time in milliseconds to trigger the callback.
            callback (Callable[[float], Any]): The function to call with the passed time information.
        """
        super().__init__()
        self.time_interval_ms = time_interval_ms 
        self.callback = callback  
        self.passed_time = None  
        self.running = True  

    def get_passed_time_ms(self) -> float:
        """
        Retrieves the amount of time (in milliseconds) that has passed since the start of the timer.

        Returns:
            float: The amount of time in milliseconds that has passed.
        """
        return self.passed_time

    def stop(self) -> None:
        """
        Stops the timer by setting the running flag to False.
        This will cause the timer thread to exit its main loop.
        """
        self.running = False

    def run(self) -> None:
        """
        The method that is run when the thread starts. This method keeps track of time and triggers
        the callback function at the specified intervals. It continues running until `stop()` is called.
        """
        start_time_ms = time.perf_counter() * 1000
        interval_number = 1 

        while self.running:
            # Calculate the target time for the next callback based on the interval and the start time.
            target_time_ms = start_time_ms + (self.time_interval_ms * interval_number)

            current_time_ms = time.perf_counter() * 1000

            self.passed_time = current_time_ms - start_time_ms

            if current_time_ms >= target_time_ms:
                # Call the provided callback function with the current time and passed time.
                self.callback({"current_time_ms": current_time_ms, "passed_time_ms": self.passed_time})
                interval_number += 1
    
            time.sleep(0.01)


