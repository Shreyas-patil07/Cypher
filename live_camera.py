import cv2
from ultralytics import YOLO
import os
import time
import winsound

MODEL_PATH = 'weapon_detection.pt'
OUTPUT_DIR = 'video_results/live'
CAMERA_INDEX = 0  # change to 1/2... if you have multiple cameras
CONF_THRESHOLD = 0.45  # raise to reduce false positives
IOU_THRESHOLD = 0.45
MIN_BOX_AREA = 2500  # ignore tiny boxes (pixels^2)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

os.makedirs(OUTPUT_DIR, exist_ok=True)

model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    raise RuntimeError(f"Could not open camera index {CAMERA_INDEX}")

# Apply preferred resolution (best-effort; camera may choose closest supported)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
fps = cap.get(cv2.CAP_PROP_FPS) or 30

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_path = os.path.join(OUTPUT_DIR, 'live_capture.mp4')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Throttle audible alerts so they don't spam continuously
last_alert_time = 0.0
ALERT_COOLDOWN_SEC = 1.0
THREAT_CLASSES = {'gun'}  # add more class names if needed
THREAT_CLASSES = {
    'gun',
    'mask', 'masked_person',
    'helmet', 'person_with_helmet',
    'accident', 'crash', 'collision',
    'car_crash', 'bike_crash', 'road_accident', 'vehicle_collision'
}

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame, verbose=False, conf=CONF_THRESHOLD, iou=IOU_THRESHOLD)
        annotated = results[0].plot()

        # Detect if any threat class is present
        boxes = results[0].boxes
        names = results[0].names
        threat_detected = False

        if boxes is not None and boxes.cls is not None and boxes.xyxy is not None:
            for cls_id, xyxy in zip(boxes.cls.tolist(), boxes.xyxy.tolist()):
                label = names.get(int(cls_id))
                if label not in THREAT_CLASSES:
                    continue
                x1, y1, x2, y2 = xyxy
                area = max(0.0, (x2 - x1)) * max(0.0, (y2 - y1))
                if area < MIN_BOX_AREA:
                    continue
                threat_detected = True
                break

        if threat_detected:
            # Visual threat banner
            cv2.rectangle(annotated, (0, 0), (width, 60), (0, 0, 255), -1)
            cv2.putText(annotated, 'THREAT DETECTED', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)
            # Audible alert (Windows)
            now = time.time()
            if now - last_alert_time >= ALERT_COOLDOWN_SEC:
                winsound.Beep(1200, 350)
                last_alert_time = now

        cv2.imshow('Live Detection - press q to quit', annotated)
        out.write(annotated)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    out.release()
    cv2.destroyAllWindows()

print(f"Saved recording to: {output_path}")
