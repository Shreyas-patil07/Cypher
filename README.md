# AI Smart Surveillance (Detection Module)

This project implements the **OpenCV + YOLO** real-time detection part for smart surveillance.

Scope included:
- Live CCTV/webcam/RTSP frame processing.
- YOLO object detection on each frame.
- Real-time bounding boxes and threat status overlay (`THREAT` / `CLEAR`).

Scope intentionally excluded:
- Notification systems.
- SMS/phone alerts.
- Law-enforcement dispatch integrations.

## 1. Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Run

```powershell
python detector.py --source 0 --model models/yolov8n.pt --threat-classes person
```

If `models/yolov8n.pt` is not present, the script falls back to `yolov8n.pt` and downloads it automatically.

## 3. RTSP Example

```powershell
python detector.py --source "rtsp://username:password@camera-ip:554/stream1" --model models/yolov8n.pt --threat-classes person
```

## 4. Custom Threat Labels

Use your trained model labels for better threat detection:

```powershell
python detector.py --source 0 --model models/custom_threat.pt --threat-classes knife,gun,weapon
```

## 5. Controls

- Press `q` to quit.

## 6. Notes

- `yolov8n.pt` is a general model and may not detect weapons reliably.
- For production-grade surveillance, train/fine-tune a domain model on threat classes.
