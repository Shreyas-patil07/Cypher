"""Local alert queue for offline mode."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List

from .alert_manager import AlertDocument


@dataclass
class LocalAlertQueue:
    """Queues alert documents locally when backend is unavailable."""

    path: Path
    max_size: int = 100
    _queue: List[AlertDocument] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text())
                self._queue = [self._from_dict(item) for item in raw]
            except Exception:
                self._queue = []

    def enqueue(self, document: AlertDocument) -> None:
        if len(self._queue) >= self.max_size:
            self._queue.pop(0)  # drop oldest
        self._queue.append(document)
        self._persist()

    def flush(self, handler) -> int:
        """Attempt to process queued alerts via provided handler(document)."""
        processed = 0
        remaining: List[AlertDocument] = []
        for doc in self._queue:
            try:
                handler(doc)
                processed += 1
            except Exception:
                remaining.append(doc)
        self._queue = remaining
        self._persist()
        return processed

    def _persist(self) -> None:
        payload = [self._to_dict(doc) for doc in self._queue]
        self.path.write_text(json.dumps(payload, default=str))

    @staticmethod
    def _to_dict(doc: AlertDocument) -> dict:
        data = asdict(doc)
        data["timestamp"] = doc.timestamp.isoformat()
        return data

    @staticmethod
    def _from_dict(data: dict) -> AlertDocument:
        return AlertDocument(
            event_id=data["event_id"],
            event_type=data["event_type"],
            risk_level=data["risk_level"],
            camera_id=data["camera_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            confidence=data["confidence"],
            image_url=data.get("image_url"),
            metadata=data.get("metadata", {}),
        )
