"""YOLOv8 detector wrapper for the CYPHER pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

import numpy as np
from ultralytics import YOLO

from .models import Detection


@dataclass
class YOLODetectorConfig:
    model_path: str = "models/yolov8n.pt"
    confidence: float = 0.5
    target_classes: Sequence[str] | None = None  # None means all classes


class YOLODetector:
    def __init__(self, config: YOLODetectorConfig) -> None:
        self.config = config
        self.model = self._load_model(config.model_path)

    @staticmethod
    def _load_model(model_path: str) -> YOLO:
        path = Path(model_path)
        if not path.exists():
            return YOLO("yolov8n.pt")
        return YOLO(str(path))

    def detect(self, frame: np.ndarray) -> List[Detection]:
        results_list = self.model.predict(source=frame, conf=self.config.confidence, verbose=False, stream=False)
        results = results_list[0]

        detections: List[Detection] = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            score = float(box.conf[0])
            label = results.names.get(cls_id, str(cls_id))
            if self.config.target_classes and label not in self.config.target_classes:
                continue
            x1, y1, x2, y2 = map(float, box.xyxy[0])
            detections.append(Detection(bbox=(x1, y1, x2, y2), confidence=score, class_id=cls_id, class_name=label))
        return detections
