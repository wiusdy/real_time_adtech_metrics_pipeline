from datetime import datetime
import time


class Monitoring:
    """
    Simple monitoring utility for logging and metrics.
    """

    @staticmethod
    def log(message: str):
        print(f"[{datetime.utcnow()}] {message}")

    @staticmethod
    def track_execution(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()

            print(f"[METRIC] Execution time: {end - start:.4f}s")
            return result

        return wrapper
