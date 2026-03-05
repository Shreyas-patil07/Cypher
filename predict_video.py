from ultralytics import YOLO
import os
import sys
import cv2
import time
import winsound

# Path to the trained model (update if needed)
MODEL_PATH = 'weapon_detection.pt'  # or 'teeth_detection_model.pt' if that's your latest
OUTPUT_DIR = 'video_results'
VIDEO_PATH = r'C:\Users\rijul\Downloads\The_Contractor_2022_-_Best_Combat_Scenes_1080P.mp4'  # default; can override with CLI arg
CONF_THRESHOLD = 0.45
IOU_THRESHOLD = 0.45
MIN_BOX_AREA = 2500  # pixels^2; ignore tiny boxes
THREAT_CLASSES = {
    'gun',
    'mask', 'masked_person',
    'helmet', 'person_with_helmet',
    'accident', 'crash', 'collision',
    'car_crash', 'bike_crash', 'road_accident', 'vehicle_collision'
}
ALERT_COOLDOWN_SEC = 1.0
if len(sys.argv) > 1:
    VIDEO_PATH = sys.argv[1]

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the trained model
model = YOLO(MODEL_PATH)

# Open the video file
cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise RuntimeError(f"Could not open video: {VIDEO_PATH}")

# Get video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
fps = cap.get(cv2.CAP_PROP_FPS) or 25

# Output video writer
output_path = os.path.join(OUTPUT_DIR, 'annotated', 'annotated_video.mp4')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

last_alert_time = 0.0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    # Run inference on the frame
    results = model(frame, verbose=False, conf=CONF_THRESHOLD, iou=IOU_THRESHOLD)
    annotated_frame = results[0].plot()

    # Threat detection overlay
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
        cv2.rectangle(annotated_frame, (0, 0), (width, 60), (0, 0, 255), -1)
        cv2.putText(annotated_frame, 'THREAT DETECTED', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)
        now = time.time()
        if now - last_alert_time >= ALERT_COOLDOWN_SEC:
            winsound.Beep(1200, 350)
            last_alert_time = now
    # Resize for live preview
    preview_frame = cv2.resize(annotated_frame, (1280, 720))
    # Show live preview
    cv2.imshow('Live Preview', preview_frame)
    # Write frame to output video
    out.write(annotated_frame)
    # Press 'q' to quit early
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Processed video: {VIDEO_PATH}\nAnnotated video saved at: {output_path}") 