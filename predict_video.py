from ultralytics import YOLO
import sys
import cv2
import time
import winsound

from video_utils import prepare_video_io, preview_and_save

# Path to the trained model (car/accident damage)
MODEL_PATH = 'car_damage_detection_model.pt'
OUTPUT_DIR = 'video_results'
VIDEO_PATH = r'C:\Users\rijul\Downloads\car accident.mp4'  # default; can override with CLI arg
CONF_THRESHOLD = 0.35
IOU_THRESHOLD = 0.45
MIN_BOX_AREA = 1200  # pixels^2; ignore tiny boxes and small blobs
# Only flag these classes
THREAT_CLASSES = {'Car-Damage'}
ALERT_COOLDOWN_SEC = 1.0
if len(sys.argv) > 1:
    VIDEO_PATH = sys.argv[1]

model = YOLO(MODEL_PATH)

cap, out, output_path, width, height, fps = prepare_video_io(
    VIDEO_PATH,
    OUTPUT_DIR,
    output_name='annotated_video.mp4',
    fallback_size=(1280, 720),
    fallback_fps=25,
)

last_alert_time = 0.0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    # Run inference on the frame
    results = model(frame, verbose=False, conf=CONF_THRESHOLD, iou=IOU_THRESHOLD)
    annotated_frame = results[0].plot()

    # Threat/damage detection overlay
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
        cv2.putText(annotated_frame, 'DAMAGE DETECTED', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)
        now = time.time()
        if now - last_alert_time >= ALERT_COOLDOWN_SEC:
            winsound.Beep(1200, 350)
            last_alert_time = now
    preview_and_save(annotated_frame, out, preview_size=(1280, 720))
    # Press 'q' to quit early
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Processed video: {VIDEO_PATH}\nAnnotated video saved at: {output_path}") 