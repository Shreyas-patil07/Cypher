"""Alert management pipeline orchestration.

The alert manager coordinates the final stage of the detection pipeline:
- Capture and encode incident frames.
- Upload evidence to persistent storage.
- Create structured alert documents in Appwrite (or any backing store).
- Fan out to downstream channels such as realtime dashboards and SMS.

This module deliberately relies on narrow protocol-style abstractions so it can
be integrated with different infrastructure layers during the hackathon.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol, Sequence

import cv2
import numpy as np

from .sms_agent import AlertEvent, SMSAgent, SMSDispatchRecord


class IncidentStorageClient(Protocol):
    """Interface for uploading incident imagery."""

    def upload(self, *, filename: str, data: bytes, content_type: str) -> str:
        """Upload binary image data and return a public or signed URL."""


class AlertRepository(Protocol):
    """Interface for persisting alert documents."""

    def create(self, document: "AlertDocument") -> str:
        """Persist alert metadata and return document ID."""


class RealtimePublisher(Protocol):
    """Publishes alert payloads to dashboards/clients."""

    def publish(self, document: "AlertDocument") -> None:
        ...


class ImageEncoder(Protocol):
    """Encodes frames into binary payloads."""

    def encode(self, frame: np.ndarray) -> tuple[bytes, str]:
        """Return (data, mime_type)."""


@dataclass
class AlertDocument:
    """Serialized alert metadata ready for persistence."""

    event_id: str
    event_type: str
    risk_level: str
    camera_id: str
    timestamp: datetime
    confidence: float
    image_url: str | None
    metadata: dict[str, str]


@dataclass
class AlertManagerResult:
    """Aggregated outcome of alert processing."""

    document_id: str | None
    image_url: str | None
    sms_records: Sequence[SMSDispatchRecord]


class OpenCVJpegEncoder:
    """Encode frames using OpenCV with configurable quality."""

    def __init__(self, *, quality: int = 85) -> None:
        self.quality = quality

    def encode(self, frame: np.ndarray) -> tuple[bytes, str]:
        success, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.quality])
        if not success:  # pragma: no cover - dependent on OpenCV internals
            raise RuntimeError("Failed to encode frame as JPEG")
        return buffer.tobytes(), "image/jpeg"


class AlertManager:
    """Coalesce alert side-effects (storage, DB, realtime, SMS)."""

    def __init__(
        self,
        *,
        storage_client: IncidentStorageClient | None = None,
        alert_repository: AlertRepository | None = None,
        realtime_publisher: RealtimePublisher | None = None,
        sms_agent: SMSAgent | None = None,
        image_encoder: ImageEncoder | None = None,
    ) -> None:
        self.storage_client = storage_client
        self.alert_repository = alert_repository
        self.realtime_publisher = realtime_publisher
        self.sms_agent = sms_agent
        self.image_encoder = image_encoder or OpenCVJpegEncoder()

    def process_event(self, event: AlertEvent, frame: np.ndarray | None = None) -> AlertManagerResult:
        """Persist the alert and fan out notifications."""

        image_url = self._handle_image_upload(event, frame)
        document_id = self._handle_alert_document(event, image_url)
        sms_records = self._handle_sms(event)
        return AlertManagerResult(document_id=document_id, image_url=image_url, sms_records=sms_records)

    def _handle_image_upload(self, event: AlertEvent, frame: np.ndarray | None) -> str | None:
        if frame is None or self.storage_client is None:
            return None
        payload, mime_type = self.image_encoder.encode(frame)
        filename = self._build_filename(event)
        return self.storage_client.upload(filename=filename, data=payload, content_type=mime_type)

    def _handle_alert_document(self, event: AlertEvent, image_url: str | None) -> str | None:
        if self.alert_repository is None:
            return None
        document = AlertDocument(
            event_id=event.event_id,
            event_type=event.event_type,
            risk_level=event.risk_level.value,
            camera_id=event.camera_id,
            timestamp=event.timestamp,
            confidence=event.confidence,
            image_url=image_url,
            metadata=event.metadata,
        )
        document_id = self.alert_repository.create(document)
        if self.realtime_publisher:
            self.realtime_publisher.publish(document)
        return document_id

    def _handle_sms(self, event: AlertEvent) -> Sequence[SMSDispatchRecord]:
        if self.sms_agent is None:
            return []
        return self.sms_agent.process_event(event)

    @staticmethod
    def _build_filename(event: AlertEvent) -> str:
        timestamp = event.timestamp.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S")
        safe_type = event.event_type.replace(" ", "_").lower()
        safe_camera = event.camera_id.replace(" ", "_").lower()
        return f"{safe_type}_{safe_camera}_{timestamp}_{event.event_id}.jpg"
