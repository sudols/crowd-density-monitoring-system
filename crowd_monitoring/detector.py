from ultralytics import YOLO


def load_model(model_name: str) -> YOLO:
    return YOLO(model_name)


def detect_people(model: YOLO, frame, confidence: float, person_class: int) -> list:
    results = model(frame, conf=confidence, verbose=False)
    people = []

    for result in results:
        for box in result.boxes:
            if int(box.cls[0]) == person_class:
                people.append(box)

    return people
