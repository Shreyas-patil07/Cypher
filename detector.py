"""YOLOv8 + OpenCV live threat detection.

Notification and SMS alerting are intentionally excluded.
This script focuses only on real-time detection and on-screen marking.
"""
import argparse
import time
from pathlib import Path

import cv2
from ultralytics import YOLO

DEFAULT_MODEL_PATH = Path("models/yolov8n.pt")
DEFAULT_SOURCE = "0"
DEFAULT_THREAT_CLASSES = {"person"}
DEFAULT_CONF_THRESHOLD = 0.35
DEFAULT_NMS_IOU_THRESHOLD = 0.45


def load_model(model_path: Path) -> YOLO:
    if not model_path.exists():
        # Fallback to hub model name (downloads on first run)
        return YOLO("yolov8n.pt")
    return YOLO(str(model_path))


def parse_source(source: str):
    """Use webcam index if source is numeric, else treat as video/RTSP path."""
    return int(source) if source.isdigit() else source


def draw_detections(frame, results, threat_classes: set[str], conf_threshold: float, draw: bool) -> bool:
    """Optionally draw boxes and return True if a threat class is present."""
    threat_seen = False
    for box in results.boxes:
        cls_id = int(box.cls[0])
        score = float(box.conf[0])
        label = results.names.get(cls_id, str(cls_id))
        if score < conf_threshold:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        color = (0, 255, 0)
        if label in threat_classes:
            color = (0, 0, 255)
            threat_seen = True

        if draw:
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame,
                f"{label} {score:.2f}",
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
                cv2.LINE_AA,
            )
    return threat_seen


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="YOLOv8 + OpenCV threat detector")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Camera index (e.g. 0) or RTSP/file path")
    parser.add_argument("--model", default=str(DEFAULT_MODEL_PATH), help="Path to YOLO model weights")
    parser.add_argument(
        "--threat-classes",
        default=",".join(sorted(DEFAULT_THREAT_CLASSES)),
        help="Comma-separated labels considered threats (e.g. knife,gun,weapon)",
    )
    parser.add_argument("--conf", type=float, default=DEFAULT_CONF_THRESHOLD, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=DEFAULT_NMS_IOU_THRESHOLD, help="NMS IoU threshold")
    parser.add_argument("--no-overlay", action="store_true", help="Hide boxes/text for a clean display")
    return parser


def main():
    args = build_parser().parse_args()

    model = load_model(Path(args.model))
    source = parse_source(args.source)
    threat_classes = {item.strip() for item in args.threat_classes.split(",") if item.strip()}

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video source: {source}")

    fps_last = time.time()
    threat_active = False
    print("Running detection loop. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame grab failed; exiting")
            break

        # Run inference
        results_list = model.predict(
            source=frame,
            conf=args.conf,
            iou=args.iou,
            verbose=False,
            stream=False,
        )

        # YOLO returns a list even for a single image
        results = results_list[0]
        threat_active = draw_detections(frame, results, threat_classes, args.conf, draw=not args.no_overlay)

        if not args.no_overlay:
            status = "THREAT" if threat_active else "CLEAR"
            status_color = (0, 0, 255) if threat_active else (0, 200, 0)
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, status_color, 2, cv2.LINE_AA)

            now = time.time()
            fps = 1.0 / max(now - fps_last, 1e-4)
            fps_last = now
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow("YOLO Threat Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
