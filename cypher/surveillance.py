"""Main surveillance loop orchestrating detection and alerting."""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Deque, Dict, Iterable, List, Optional

import numpy as np

from cypher.alerts import AlertEvent, AlertManager, RiskLevel as SmsRiskLevel
from cypher.config import Settings
from cypher.detection import (
    EventConfig,
    EventDetectionEngine,
    MultiFrameConfirmation,
    PersonEvent,
    RiskLevel,
    RiskScorer,
    WeaponEvent,
    YOLODetector,
    YOLODetectorConfig,
)
from cypher.vision import FrameCapture, FramePreprocessor

LOG = logging.getLogger(__name__)


class GlobalRateLimiter:
    """Simple sliding window limiter for confirmed alerts."""

    def __init__(self, *, max_per_minute: int) -> None:
        self.max_per_minute = max_per_minute
        self.window: Deque[float] = deque()

    def allow(self, now: float | None = None) -> bool:
        now = now or time.time()
        cutoff = now - 60.0
        while self.window and self.window[0] < cutoff:
            self.window.popleft()
        if len(self.window) >= self.max_per_minute:
            return False
        self.window.append(now)
        return True


@dataclass
class SurveillanceStats:
    """Live statistics tracked during surveillance."""

    frames_processed: int = 0
    alerts_created: int = 0
    threats_by_type: Dict[str, int] = field(default_factory=lambda: {"person": 0, "weapon": 0})
    start_time: Optional[float] = None
    last_alert_timestamp: Optional[str] = None
    current_fps: float = 0.0
    consecutive_errors: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    @property
    def uptime_seconds(self) -> float:
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def record_frame(self) -> None:
        with self._lock:
            self.frames_processed += 1

    def record_alert(self, event_type: str) -> None:
        with self._lock:
            self.alerts_created += 1
            self.threats_by_type[event_type] = self.threats_by_type.get(event_type, 0) + 1
            self.last_alert_timestamp = datetime.now(timezone.utc).isoformat()

    def update_fps(self, fps: float) -> None:
        with self._lock:
            self.current_fps = round(fps, 1)

    def reset(self) -> None:
        with self._lock:
            self.frames_processed = 0
            self.alerts_created = 0
            self.threats_by_type = {"person": 0, "weapon": 0}
            self.start_time = time.time()
            self.last_alert_timestamp = None
            self.current_fps = 0.0
            self.consecutive_errors = 0

    def snapshot(self) -> dict:
        """Return a JSON-safe copy of current stats."""
        with self._lock:
            return {
                "frames_processed": self.frames_processed,
                "alerts_created": self.alerts_created,
                "threats_by_type": dict(self.threats_by_type),
                "system_uptime_seconds": self.uptime_seconds,
                "last_alert_timestamp": self.last_alert_timestamp,
                "current_fps": self.current_fps,
                "total_threats": self.alerts_created,
                "active_cameras": 1 if self.start_time is not None else 0,
            }


class SurveillanceSystem:
    def __init__(
        self,
        *,
        settings: Settings,
        alert_manager: AlertManager,
        detector_config: Optional[YOLODetectorConfig] = None,
    ) -> None:
        self.settings = settings
        self.alert_manager = alert_manager
        self.stats = SurveillanceStats()
        self.detector = YOLODetector(detector_config or YOLODetectorConfig())
        self.preprocessor = FramePreprocessor(target_size=(settings.frame_size, settings.frame_size))
        self.capture = FrameCapture(settings.video_source, skip_frames=settings.frame_skip)
        self.event_engine = EventDetectionEngine(
            EventConfig(
                person_confidence_threshold=settings.person_confidence_threshold,
                person_confirmation_frames=settings.person_confirmation_frames,
                weapon_simulation_enabled=settings.weapon_simulation_enabled,
                weapon_simulation_rate=settings.weapon_simulation_rate,
            )
        )
        self.confirmation = MultiFrameConfirmation(
            thresholds={"person": settings.person_confirmation_frames, "weapon": 1}
        )
        self.risk_scorer = RiskScorer()
        self.rate_limiter = GlobalRateLimiter(max_per_minute=10)
        self._stop_event = threading.Event()

    def start(self) -> None:
        self._stop_event.clear()
        self.stats.reset()
        self._run_loop()

    def stop(self) -> None:
        self._stop_event.set()
        self.capture.release()

    def _run_loop(self) -> None:
        fps_timer = time.time()
        frame_count_for_fps = 0

        while not self._stop_event.is_set():
            try:
                ret, frame = self.capture.read_frame()
                if not ret:
                    LOG.warning("Frame read failed; ending loop")
                    break

                self.stats.record_frame()
                self.stats.consecutive_errors = 0
                frame_count_for_fps += 1

                # Calculate FPS every second
                elapsed = time.time() - fps_timer
                if elapsed >= 1.0:
                    self.stats.update_fps(frame_count_for_fps / elapsed)
                    frame_count_for_fps = 0
                    fps_timer = time.time()

                processed, original_shape = self.preprocessor.preprocess(frame)
                detections = self.detector.detect(processed)

                person_events = self.event_engine.detect_person(detections)
                weapon_events = self.event_engine.detect_weapon_simulated(person_events)
                all_events = person_events + weapon_events

                confirmed_events, _ = self.confirmation.update(all_events)
                confirmed_events = self._apply_risk(confirmed_events)

                for event in confirmed_events:
                    if not self.rate_limiter.allow():
                        continue
                    alert_event = self._to_alert_event(event)
                    self.alert_manager.process_event(alert_event, frame=frame)
                    self.stats.record_alert(event.event_type)

            except Exception:
                LOG.exception("Error processing frame")
                self.stats.consecutive_errors += 1
                if self.stats.consecutive_errors >= 10:
                    LOG.error("10 consecutive errors; stopping surveillance")
                    break

        self.capture.release()

    def _apply_risk(self, events: Iterable[PersonEvent | WeaponEvent]):
        enriched = []
        for event in events:
            risk = self.risk_scorer.score(event)
            if isinstance(event, WeaponEvent):
                enriched.append(
                    WeaponEvent(
                        event_type=event.event_type,
                        confidence=event.confidence,
                        timestamp=event.timestamp,
                        bbox=event.bbox,
                        weapon_type=event.weapon_type,
                        risk_level=risk,
                        metadata=event.metadata,
                    )
                )
            else:
                enriched.append(
                    PersonEvent(
                        event_type=event.event_type,
                        confidence=event.confidence,
                        timestamp=event.timestamp,
                        bbox=event.bbox,
                        risk_level=risk,
                        metadata=event.metadata,
                    )
                )
        return enriched

    @staticmethod
    def _to_alert_event(event: PersonEvent | WeaponEvent) -> AlertEvent:
        sms_risk = SmsRiskLevel[event.risk_level.name]
        return AlertEvent(
            event_id=f"{int(time.time()*1000)}",
            event_type=event.event_type,
            risk_level=sms_risk,
            camera_id="Camera-1",
            timestamp=event.timestamp,
            confidence=event.confidence,
            metadata={**event.metadata, "weapon_type": getattr(event, "weapon_type", "")},
        )
