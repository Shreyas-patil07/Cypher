"""Minimal training entrypoint for a custom YOLOv8 model.

Usage (PowerShell):
    .\.venv\Scripts\python.exe train.py

Adjust paths or hyperparameters below as needed before running.
"""
from pathlib import Path
from ultralytics import YOLO

# Paths
DATA_YAML = Path("datasets/threats/data.yaml")
BASE_MODEL = "yolov8n.pt"  # change to yolov8s.pt if you have more compute
EPOCHS = 50
IMG_SIZE = 640
BATCH = 16


def main():
    model = YOLO(BASE_MODEL)
    model.train(data=str(DATA_YAML), epochs=EPOCHS, imgsz=IMG_SIZE, batch=BATCH)

    # Best weights will be saved under runs/detect/exp*/weights/best.pt


if __name__ == "__main__":
    main()
