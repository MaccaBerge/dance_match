import time
import threading
from typing import Callable, Any


class Timer_Thread(threading.Thread):
    def __init__(self, time_interval_ms: float, callback: Callable[[float], Any]) -> None:
        super().__init__()
        self.time_interval_ms = time_interval_ms
        self.callback = callback

        self.passed_time = None

        self.running = True
    
    def get_passed_time_ms(self) -> float:
        return self.passed_time

    def stop(self) -> None:
        self.running = False
    
    def run(self) -> None:
        start_time_ms = time.perf_counter() * 1000
        interval_number = 1
        while self.running:
            target_time_ms = start_time_ms + (self.time_interval_ms * interval_number)
            current_time_ms = time.perf_counter() * 1000
            self.passed_time = current_time_ms-start_time_ms
            if current_time_ms >= target_time_ms:
                self.callback({"current_time_ms": current_time_ms, "passed_time_ms": self.passed_time})
                interval_number += 1
            time.sleep(0.01)

