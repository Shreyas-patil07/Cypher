"""Alerting and notification logic for CYPHER."""

from .alert_manager import (
	AlertDocument,
	AlertManager,
	AlertManagerResult,
	AlertRepository,
	ImageEncoder,
	IncidentStorageClient,
	OpenCVJpegEncoder,
	RealtimePublisher,
)
from .adapters import AppwriteAlertRepository, AppwriteStorageAdapter, NoopRealtimePublisher
from .queue import LocalAlertQueue
from .sms_agent import (
	AlertEvent,
	AppwriteSMSClient,
	InMemoryHistoryStore,
	RateLimiter,
	RiskLevel,
	SMSAgent,
	SMSAgentConfig,
	SMSDispatchRecord,
)

__all__ = [
	"AppwriteAlertRepository",
	"AppwriteStorageAdapter",
	"AlertDocument",
	"AlertManager",
	"AlertManagerResult",
	"AlertEvent",
	"AlertRepository",
	"AppwriteSMSClient",
	"ImageEncoder",
	"InMemoryHistoryStore",
	"IncidentStorageClient",
	"LocalAlertQueue",
	"NoopRealtimePublisher",
	"OpenCVJpegEncoder",
	"RateLimiter",
	"RealtimePublisher",
	"RiskLevel",
	"SMSAgent",
	"SMSAgentConfig",
	"SMSDispatchRecord",
]
