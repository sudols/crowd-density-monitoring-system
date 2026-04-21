import cv2


class MotionSpoofFilter:
    def __init__(self, motion_threshold=0.01, static_frames=15, min_box_size=20, key_grid=20, diff_threshold=25):
        self.motion_threshold = motion_threshold
        self.static_frames = static_frames
        self.min_box_size = min_box_size
        self.key_grid = key_grid
        self.diff_threshold = diff_threshold
        self.static_counts = {}

    def filter_people(self, frame, previous_frame, people):
        if previous_frame is None:
            self.static_counts = {}
            return list(people), []

        valid_people = []
        blocked_people = []
        next_counts = {}
        frame_height, frame_width = frame.shape[:2]

        for person in people:
            x1, y1, x2, y2 = map(int, person.xyxy[0])
            x1 = max(0, min(x1, frame_width - 1))
            y1 = max(0, min(y1, frame_height - 1))
            x2 = max(0, min(x2, frame_width))
            y2 = max(0, min(y2, frame_height))

            box_width = x2 - x1
            box_height = y2 - y1
            if box_width < self.min_box_size or box_height < self.min_box_size:
                valid_people.append(person)
                continue

            motion_ratio = self._motion_ratio(frame, previous_frame, x1, y1, x2, y2)
            key = self._box_key(x1, y1, x2, y2)

            if motion_ratio < self.motion_threshold:
                static_streak = self.static_counts.get(key, 0) + 1
            else:
                static_streak = 0

            next_counts[key] = static_streak

            if static_streak >= self.static_frames:
                blocked_people.append(person)
            else:
                valid_people.append(person)

        self.static_counts = next_counts
        return valid_people, blocked_people

    def _motion_ratio(self, frame, previous_frame, x1, y1, x2, y2):
        current_roi = frame[y1:y2, x1:x2]
        previous_roi = previous_frame[y1:y2, x1:x2]
        if current_roi.size == 0 or previous_roi.size == 0:
            return 1.0

        current_gray = cv2.cvtColor(current_roi, cv2.COLOR_BGR2GRAY)
        previous_gray = cv2.cvtColor(previous_roi, cv2.COLOR_BGR2GRAY)
        current_gray = cv2.GaussianBlur(current_gray, (5, 5), 0)
        previous_gray = cv2.GaussianBlur(previous_gray, (5, 5), 0)

        difference = cv2.absdiff(current_gray, previous_gray)
        _, difference_mask = cv2.threshold(difference, self.diff_threshold, 255, cv2.THRESH_BINARY)

        changed_pixels = cv2.countNonZero(difference_mask)
        total_pixels = difference_mask.size
        if total_pixels == 0:
            return 1.0

        return changed_pixels / float(total_pixels)

    def _box_key(self, x1, y1, x2, y2):
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        area_bucket = ((x2 - x1) * (y2 - y1)) // (self.key_grid * self.key_grid)
        return center_x // self.key_grid, center_y // self.key_grid, area_bucket
