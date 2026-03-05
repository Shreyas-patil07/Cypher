"""Video frame capture with optional frame skipping."""

from __future__ import annotations

import cv2


class FrameCapture:
    def __init__(self, source: str | int, skip_frames: int = 0) -> None:
        self.source = source
        self.skip_frames = max(0, int(skip_frames))
        self._cap = cv2.VideoCapture(source)
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open video source: {source}")
        self._skip_counter = 0

    def read_frame(self):
        # Implement frame skipping to reduce load.
        if self.skip_frames > 0:
            while self._skip_counter < self.skip_frames:
                self._cap.read()
                self._skip_counter += 1
            self._skip_counter = 0
        ret, frame = self._cap.read()
        return ret, frame

    def release(self) -> None:
        if self._cap:
            self._cap.release()

    def get_fps(self) -> float:
        return float(self._cap.get(cv2.CAP_PROP_FPS) or 0.0)
