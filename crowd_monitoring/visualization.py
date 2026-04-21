import cv2


def draw_info(
    frame,
    count,
    status,
    color,
    green_max,
    alert_msg,
    show_boxes,
    boxes,
    live_state,
    live_message,
    live_color,
    blocked_boxes,
    spoof_label,
):
    cv2.rectangle(frame, (10, 10), (360, 190), (0, 0, 0), -1)
    cv2.rectangle(frame, (10, 10), (360, 190), color, 3)

    cv2.putText(frame, f"Count: {count}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Status: {status}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(frame, f"Green: 0-{green_max}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(frame, f"Liveness: {live_state}", (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.55, live_color, 2)
    cv2.putText(frame, live_message, (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)

    if status == "RED":
        h = frame.shape[0]
        cv2.rectangle(frame, (10, h - 60), (frame.shape[1] - 10, h - 10), (0, 0, 255), -1)
        cv2.putText(frame, alert_msg, (20, h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    if show_boxes:
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        for box in blocked_boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            text_y = y1 - 10 if y1 > 20 else y1 + 20
            cv2.putText(frame, spoof_label, (x1, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    return frame
