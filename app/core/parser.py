import os
import json
import cv2
from datetime import datetime
from ultralytics import YOLO
from app.core.agents import filter_agent, journal_agent

# Config Paths
CAPTURED_IMAGES_DIR = "static/captured"
JSON_FILE = "captured_images.json"
CLASS_NAMES_FILE = "captured_class_names.json"

os.makedirs(CAPTURED_IMAGES_DIR, exist_ok=True)


async def get_valid_classes(user_prompt: str) -> list:
    response = await filter_agent.run(user_prompt=user_prompt)
    return [word.strip().lower() for word in response.output.split(",")]


def reset_captured_data():
    """Deletes stored logs and images."""
    for path in [JSON_FILE, CLASS_NAMES_FILE]:
        if os.path.exists(path):
            os.remove(path)

    for file in os.listdir(CAPTURED_IMAGES_DIR):
        os.remove(os.path.join(CAPTURED_IMAGES_DIR, file))


def save_detections(image, detections, class_names):
    highest_conf_per_class = {}
    detected_class_ids = set()

    for det in detections:
        class_id = int(det.cls[0])
        conf = float(det.conf[0])

        if conf > 0.7 and (class_id not in highest_conf_per_class or conf > highest_conf_per_class[class_id]["conf"]):
            highest_conf_per_class[class_id] = {
                "conf": conf, "image": image.copy()}
            detected_class_ids.add(class_id)

    if not highest_conf_per_class:
        return

    try:
        with open(JSON_FILE, "r") as f:
            image_log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        image_log = {}

    for class_id, data in highest_conf_per_class.items():
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
        image_path = os.path.join(
            CAPTURED_IMAGES_DIR, f"class_{class_id}_{timestamp}.jpg")
        cv2.imwrite(image_path, data["image"])
        image_log[class_id] = {"path": image_path, "conf": data["conf"]}

    with open(JSON_FILE, "w") as f:
        json.dump(image_log, f, indent=4)

    # Update class names file
    new_names = [class_names[cid]
                 for cid in detected_class_ids if cid < len(class_names)]

    try:
        with open(CLASS_NAMES_FILE, "r") as f:
            existing_names = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_names = []

    updated_names = list(set(existing_names + new_names))
    with open(CLASS_NAMES_FILE, "w") as f:
        json.dump(updated_names, f, indent=4)


async def run_detection_on_video(video_path: str, situation: str, model_path: str = "yolo11n.pt"):
    model = YOLO(model_path)
    all_class_names = list(model.names.values())

    valid_class_names = await get_valid_classes(situation)
    selected_indices = [i for i, name in enumerate(
        all_class_names) if name.lower() in valid_class_names]

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError("Could not open video.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.track(frame, conf=0.75, iou=0.65, classes=selected_indices, persist=True)

        annotated_frame = results[0].plot()
        cv2.imshow("YOLOv8 Tracking", annotated_frame)
        
        save_detections(annotated_frame, results[0].boxes, all_class_names)

    cap.release()
    cv2.destroyAllWindows()


async def summarize_detected_objects(video_path: str, situation: str) -> str:
    os.remove(JSON_FILE) if os.path.exists(JSON_FILE) else None

    await run_detection_on_video(video_path, situation)

    try:
        with open(CLASS_NAMES_FILE, "r") as f:
            detected_objects = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return "No detected objects to summarize."

    if not detected_objects:
        return "No relevant objects found."

    object_list = ", ".join(detected_objects)
    response = await journal_agent.run(user_prompt=object_list)
    return response
