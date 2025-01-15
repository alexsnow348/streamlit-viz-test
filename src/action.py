import pandas as pd
import cv2

def clear_data(session_key, folder_selected, session_state):
    session_state[session_key][folder_selected] = pd.DataFrame(
        columns=["Time", "Cell Type", "Value"]
    )
    session_state[session_key][f"image_and_time_info_{folder_selected}"] = []
    session_state.play_timelapse_active = False
    session_state.current_frame_idx = 0
    return session_state

def transform_xyxy_to_minmax(x1, y1, x2, y2):
    xmin = min(x1, x2)
    ymin = min(y1, y2)
    xmax = max(x1, x2)
    ymax = max(y1, y2)
    return xmin, ymin, xmax, ymax


def transform_xywh_to_minmax(x, y, w, h):
    xmin = x - w / 2
    ymin = y - h / 2
    xmax = x + w / 2
    ymax = y + h / 2
    return xmin, ymin, xmax, ymax


def draw_detection(image, bboxes, class_labels):
    """Draw bounding boxes on the image."""
    for i, bbox in enumerate(bboxes):
        # left / top / right / bottom
        x1 = bbox["bbox_left"]
        y1 = bbox["bbox_top"]
        x2 = bbox["bbox_right"]
        y2 = bbox["bbox_bottom"]
        
        xmin, ymin, xmax, ymax = transform_xyxy_to_minmax(x1, y1, x2, y2)

        if class_labels[i].upper() == "RGB_100":
            color = (255, 0, 0)
        elif class_labels[i].upper() == "RGB_010":
            color = (0, 255, 0)
        elif class_labels[i].upper() == "RGB_001":
            color = (0, 0, 255)
        else:
            color = (255, 255, 255)
        cv2.rectangle(image, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 2)
        cv2.putText(
            image,
            class_labels[i],
            (int(xmin) - 10, int(ymin) - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
        )
    return image

