"""SMS alert agent built on top of Appwrite Messaging.

This module provides the `SMSAgent` class which is responsible for the
following responsibilities:
- Determine whether an alert meets the configured risk threshold.
- Enforce configurable, per-recipient sliding window rate limits.
- Format CYPHER alert messages for SMS delivery.
- Dispatch SMS via Appwrite Messaging (Twilio backend) and capture results.
- Persist delivery history for audit APIs (`/api/sms/history`).

It is designed to be framework-agnostic so it can be used inside a FastAPI
background task, a Celery worker, or any custom orchestration layer.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
import logging
from typing import Dict, Iterable, List, MutableMapping, Protocol, Sequence

from appwrite.client import Client
from appwrite.exception import AppwriteException
from appwrite.services.messaging import Messaging


LOG = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Normalized risk levels for alerts."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def __lt__(self, other: "RiskLevel") -> bool:  # type: ignore[override]
        order = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2, RiskLevel.CRITICAL: 3}
        return order[self] < order[other]


@dataclass(frozen=True)
class AlertEvent:
    """Normalized representation of a confirmed alert."""

    event_id: str
    event_type: str
    risk_level: RiskLevel
    camera_id: str
    timestamp: datetime
    confidence: float
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class SMSAgentConfig:
    """Runtime configuration for the SMS agent."""

    enabled: bool = False
    recipients: Sequence[str] = field(default_factory=list)
    min_risk_level: RiskLevel = RiskLevel.HIGH
    rate_limit_per_hour: int = 5
    sender_id: str | None = None

    def sanitized_recipients(self) -> List[str]:
        return [recipient.strip() for recipient in self.recipients if recipient.strip()]


@dataclass(frozen=True)
class SMSDispatchRecord:
    """Audit log entry for a dispatched (or skipped) SMS."""

    event_id: str
    recipient: str
    body: str
    status: str
    detail: str
    timestamp: datetime


class MessagingClient(Protocol):
    """Abstraction over the underlying messaging provider."""

    def send_sms(self, *, body: str, recipients: Sequence[str], sender_id: str | None = None) -> str:
        """Send an SMS message and return provider message ID."""


class SMSHistoryStore(Protocol):
    """Persistence layer for SMS dispatch records."""

    def record(self, record: SMSDispatchRecord) -> None:
        ...


class InMemoryHistoryStore:
    """Simple, non-persistent history store useful for demos and testing."""

    def __init__(self) -> None:
        self._records: list[SMSDispatchRecord] = []

    def record(self, record: SMSDispatchRecord) -> None:
        self._records.append(record)

    def list_records(self) -> list[SMSDispatchRecord]:
        return list(self._records)


class AppwriteSMSClient:
    """Minimal wrapper around Appwrite Messaging SMS API."""

    def __init__(self, *, endpoint: str, project_id: str, api_key: str) -> None:
        self._client = Client()
        self._client.set_endpoint(endpoint)
        self._client.set_project(project_id)
        self._client.set_key(api_key)
        self._messaging = Messaging(self._client)

    def send_sms(self, *, body: str, recipients: Sequence[str], sender_id: str | None = None) -> str:
        payload = {
            "content": body,
            "addresses": list(recipients),
        }
        if sender_id:
            payload["senderId"] = sender_id
        try:
            response = self._messaging.create_sms(payload)
        except AppwriteException as exc:  # pragma: no cover - depends on external service
            LOG.exception("Appwrite SMS dispatch failed")
            raise
        message_id = response.get("$id", "")
        LOG.debug("Appwrite SMS dispatched", extra={"message_id": message_id})
        return message_id


class RateLimiter:
    """Sliding window rate limiter per recipient."""

    def __init__(self, *, max_per_hour: int) -> None:
        self.max_per_hour = max_per_hour
        self._windows: MutableMapping[str, deque[datetime]] = defaultdict(deque)

    def allow(self, recipient: str, *, now: datetime | None = None) -> bool:
        if self.max_per_hour <= 0:
            return True
        now = now or datetime.now(timezone.utc)
        window_start = now - timedelta(hours=1)
        bucket = self._windows[recipient]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= self.max_per_hour:
            return False
        bucket.append(now)
        return True


class SMSAgent:
    """Coordinates risk filtering, rate limiting, and dispatch."""

    def __init__(
        self,
        *,
        config: SMSAgentConfig,
        messaging_client: MessagingClient,
        history_store: SMSHistoryStore | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        self.config = config
        self.messaging_client = messaging_client
        self.history_store = history_store or InMemoryHistoryStore()
        self.rate_limiter = rate_limiter or RateLimiter(max_per_hour=config.rate_limit_per_hour)

    def process_event(self, event: AlertEvent) -> list[SMSDispatchRecord]:
        """Process a confirmed alert and return dispatch records."""

        if not self.config.enabled:
            LOG.debug("SMS agent disabled; skipping event", extra={"event_id": event.event_id})
            return []
        if event.risk_level < self.config.min_risk_level:
            LOG.info(
                "Event below SMS risk threshold",
                extra={"event_id": event.event_id, "risk_level": event.risk_level.value},
            )
            return []

        recipients = self.config.sanitized_recipients()
        if not recipients:
            LOG.warning("SMS agent enabled but no recipients configured")
            return []

        message = self._format_message(event)
        dispatch_records: list[SMSDispatchRecord] = []

        allowed_recipients = [r for r in recipients if self.rate_limiter.allow(r)]
        skipped_recipients = set(recipients) - set(allowed_recipients)

        if skipped_recipients:
            for recipient in skipped_recipients:
                record = SMSDispatchRecord(
                    event_id=event.event_id,
                    recipient=recipient,
                    body=message,
                    status="skipped",
                    detail="rate_limit",
                    timestamp=datetime.now(timezone.utc),
                )
                self.history_store.record(record)
                dispatch_records.append(record)
            LOG.info(
                "SMS rate limit reached", extra={"recipients": sorted(skipped_recipients), "event_id": event.event_id}
            )

        if not allowed_recipients:
            return dispatch_records

        try:
            message_id = self.messaging_client.send_sms(
                body=message, recipients=allowed_recipients, sender_id=self.config.sender_id
            )
        except AppwriteException as exc:  # pragma: no cover - depends on external service
            LOG.exception("Failed to dispatch SMS", extra={"event_id": event.event_id})
            record = SMSDispatchRecord(
                event_id=event.event_id,
                recipient=",".join(allowed_recipients),
                body=message,
                status="error",
                detail=str(exc),
                timestamp=datetime.now(timezone.utc),
            )
            self.history_store.record(record)
            dispatch_records.append(record)
            return dispatch_records

        for recipient in allowed_recipients:
            record = SMSDispatchRecord(
                event_id=event.event_id,
                recipient=recipient,
                body=message,
                status="sent",
                detail=message_id,
                timestamp=datetime.now(timezone.utc),
            )
            self.history_store.record(record)
            dispatch_records.append(record)
        LOG.info(
            "SMS sent",
            extra={"event_id": event.event_id, "recipients": allowed_recipients, "message_id": message_id},
        )
        return dispatch_records

    @staticmethod
    def _format_message(event: AlertEvent) -> str:
        timestamp = event.timestamp.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
        return (
            f"[CYPHER ALERT] {event.event_type} detected at {event.camera_id} - "
            f"{timestamp} Risk: {event.risk_level.value.upper()}"
        )
