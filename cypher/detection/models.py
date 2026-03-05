"""Core data models for detection events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Tuple


BBox = Tuple[float, float, float, float]  # (x1, y1, x2, y2)


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Detection:
    bbox: BBox
    confidence: float
    class_id: int
    class_name: str


@dataclass(frozen=True)
class Event:
    event_type: str
    confidence: float
    timestamp: datetime
    bbox: BBox
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PersonEvent(Event):
    risk_level: RiskLevel = RiskLevel.MEDIUM


@dataclass(frozen=True)
class WeaponEvent(Event):
    weapon_type: str = "unknown"
    risk_level: RiskLevel = RiskLevel.HIGH


@dataclass(frozen=True)
class EventConfig:
    person_confidence_threshold: float = 0.7
    person_confirmation_frames: int = 3
    weapon_simulation_enabled: bool = False
    weapon_simulation_rate: float = 0.1
