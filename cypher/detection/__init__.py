"""Detection-related components for CYPHER."""

from .confirmation import MultiFrameConfirmation
from .event_engine import EventDetectionEngine
from .models import Detection, Event, EventConfig, PersonEvent, RiskLevel, WeaponEvent
from .risk_scorer import RiskScorer

# YOLODetector depends on ultralytics/torch; make it optional to keep imports light during tests.
try:  # pragma: no cover - exercised in integration/runtime
	from .detector import YOLODetector, YOLODetectorConfig  # type: ignore
except Exception:  # pragma: no cover
	YOLODetector = None  # type: ignore
	YOLODetectorConfig = None  # type: ignore

__all__ = [
	"Detection",
	"Event",
	"EventConfig",
	"EventDetectionEngine",
	"MultiFrameConfirmation",
	"PersonEvent",
	"RiskLevel",
	"RiskScorer",
	"WeaponEvent",
]

if YOLODetector is not None:
	__all__ += ["YOLODetector", "YOLODetectorConfig"]
