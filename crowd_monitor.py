import cv2
import numpy as np

from crowd_monitoring.config import load_config
from crowd_monitoring.density import get_status
from crowd_monitoring.detector import detect_people, load_model
from crowd_monitoring.liveness import LivenessChecker, liveness_color
from crowd_monitoring.anti_spoof import MotionSpoofFilter
from crowd_monitoring.visualization import draw_info
 
 
def main():
    config = load_config()
    model = load_model(config["model"]["name"])

    confidence = config["model"]["confidence"]
    person_class = config["model"]["person_class"]
    green_max = config["density"]["green_max"]
    yellow_max = config["density"]["yellow_max"]
    alert_msg = config["alerts"]["message"]
    show_boxes = config["video"]["show_boxes"]
    window_name = config["display"]["window_name"]
    camera_source = config["video"]["source"]

    liveness_config = config.get("liveness", {})
    liveness_enabled = liveness_config.get("enabled", True)
    liveness = LivenessChecker(
        stale_frame_seconds=liveness_config.get("stale_frame_seconds", 2.0),
        max_read_failures=liveness_config.get("max_read_failures", 10),
    )

    anti_spoof_config = config.get("anti_spoof", {})
    anti_spoof_enabled = anti_spoof_config.get("enabled", True)
    spoof_label = anti_spoof_config.get("label", "SPOOF/STATIC")
    motion_filter = MotionSpoofFilter(
        motion_threshold=anti_spoof_config.get("motion_threshold", 0.01),
        static_frames=anti_spoof_config.get("static_frames", 15),
        min_box_size=anti_spoof_config.get("min_box_size", 20),
        key_grid=anti_spoof_config.get("key_grid", 20),
        diff_threshold=anti_spoof_config.get("diff_threshold", 25),
    )
 
    cap = cv2.VideoCapture(camera_source, cv2.CAP_V4L2)
    cap.set(3, 640)
    cap.set(4, 480)
 
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return

    print("Starting... Press 'q' to quit")
    last_good_frame = None
    previous_frame = None

    while True:
        ret, frame = cap.read()

        if liveness_enabled:
            live_state, live_message = liveness.update(ret, frame)
            live_color = liveness_color(live_state)
        else:
            live_state, live_message, live_color = "DISABLED", "Liveness disabled", (150, 150, 150)

        if not ret:
            motion_filter.static_counts = {}
            if last_good_frame is not None:
                error_frame = last_good_frame.copy()
            else:
                error_frame = np.zeros((480, 640, 3), dtype=np.uint8)

            cv2.putText(error_frame, f"Liveness: {live_state}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, live_color, 2)
            cv2.putText(error_frame, live_message, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1)

            if live_state == "CRITICAL":
                cv2.putText(error_frame, "Camera disconnected or unavailable", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow(window_name, error_frame)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            continue

        last_good_frame = frame.copy()
        original_frame = frame.copy()

        people = detect_people(model, frame, confidence, person_class)

        blocked_people = []
        if anti_spoof_enabled:
            valid_people, blocked_people = motion_filter.filter_people(frame, previous_frame, people)
        else:
            valid_people = people

        count = len(valid_people)
        status, color = get_status(count, green_max, yellow_max)

        frame = draw_info(
            frame,
            count,
            status,
            color,
            green_max,
            alert_msg,
            show_boxes,
            valid_people,
            live_state,
            live_message,
            live_color,
            blocked_people,
            spoof_label,
        )

        previous_frame = original_frame
 
        cv2.imshow(window_name, frame)
 
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
 
    cap.release()
    cv2.destroyAllWindows()
 
 
if __name__ == "__main__":
    main()
