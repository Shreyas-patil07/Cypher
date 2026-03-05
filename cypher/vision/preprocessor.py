"""Frame preprocessing helpers for YOLO input and output mapping."""

from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np


class FramePreprocessor:
    def __init__(self, target_size: Tuple[int, int] = (640, 640)) -> None:
        self.target_size = target_size

    def preprocess(self, frame: np.ndarray) -> tuple[np.ndarray, tuple[int, int]]:
        original_shape = (frame.shape[0], frame.shape[1])
        resized = cv2.resize(frame, self.target_size, interpolation=cv2.INTER_LINEAR)
        return resized, original_shape

    def denormalize_coords(self, boxes: np.ndarray, original_shape: tuple[int, int]) -> np.ndarray:
        # YOLO returns boxes in xyxy relative to the resized frame; map back to original dims.
        h, w = original_shape
        scale_x = w / float(self.target_size[0])
        scale_y = h / float(self.target_size[1])
        mapped = boxes.copy()
        mapped[:, [0, 2]] *= scale_x
        mapped[:, [1, 3]] *= scale_y
        return mapped
