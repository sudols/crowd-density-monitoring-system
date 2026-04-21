import time


class LivenessChecker:
    def __init__(self, stale_frame_seconds=2.0, max_read_failures=10):
        self.stale_frame_seconds = stale_frame_seconds
        self.max_read_failures = max_read_failures
        self.last_frame_score = None
        self.last_change_time = time.time()
        self.read_failures = 0
        self.state = "HEALTHY"
        self.message = "Live"

    def update(self, ret, frame):
        now = time.time()

        if not ret or frame is None:
            self.read_failures += 1
            if self.read_failures >= self.max_read_failures:
                self.state = "CRITICAL"
                self.message = "Camera read failure"
            else:
                self.state = "WARNING"
                self.message = "Temporary frame read issue"
            return self.state, self.message

        self.read_failures = 0
        frame_score = float(frame.mean())

        if self.last_frame_score is None:
            self.last_frame_score = frame_score
            self.last_change_time = now
            self.state = "HEALTHY"
            self.message = "Live"
            return self.state, self.message

        if abs(frame_score - self.last_frame_score) > 0.5:
            self.last_frame_score = frame_score
            self.last_change_time = now
            self.state = "HEALTHY"
            self.message = "Live"
            return self.state, self.message

        stale_time = now - self.last_change_time
        if stale_time >= self.stale_frame_seconds:
            self.state = "WARNING"
            self.message = f"Possible frozen feed ({stale_time:.1f}s)"
        else:
            self.state = "HEALTHY"
            self.message = "Live"

        return self.state, self.message


def liveness_color(state):
    if state == "HEALTHY":
        return (0, 255, 0)
    if state == "WARNING":
        return (0, 255, 255)
    return (0, 0, 255)
