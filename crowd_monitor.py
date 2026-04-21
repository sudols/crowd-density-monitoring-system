import cv2

from crowd_monitoring.config import load_config
from crowd_monitoring.density import get_status
from crowd_monitoring.detector import detect_people, load_model
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
 
    cap = cv2.VideoCapture(camera_source, cv2.CAP_V4L2)
    cap.set(3, 640)
    cap.set(4, 480)
 
    if not cap.isOpened():
        print("Error: Cannot open camera")
        return
 
    print("Starting... Press 'q' to quit")
 
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
 
        people = detect_people(model, frame, confidence, person_class)
        count = len(people)
        status, color = get_status(count, green_max, yellow_max)
 
        frame = draw_info(frame, count, status, color, green_max, alert_msg, show_boxes, people)
 
        cv2.imshow(window_name, frame)
 
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
 
    cap.release()
    cv2.destroyAllWindows()
 
 
if __name__ == "__main__":
    main()
