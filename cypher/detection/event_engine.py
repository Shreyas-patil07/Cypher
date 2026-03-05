"""Event detection logic (person + simulated weapon)."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List

from .models import Detection, EventConfig, PersonEvent, RiskLevel, WeaponEvent


@dataclass
class EventDetectionEngine:
    config: EventConfig

    def detect_person(self, detections: Iterable[Detection]) -> List[PersonEvent]:
        events: List[PersonEvent] = []
        now = datetime.now(timezone.utc)
        for det in detections:
            if det.class_name != "person":
                continue
            if det.confidence < self.config.person_confidence_threshold:
                continue
            events.append(
                PersonEvent(
                    event_type="person",
                    confidence=det.confidence,
                    timestamp=now,
                    bbox=det.bbox,
                    risk_level=RiskLevel.MEDIUM,
                    metadata={"class_id": str(det.class_id)},
                )
            )
        return events

    def detect_weapon_simulated(self, person_events: Iterable[PersonEvent]) -> List[WeaponEvent]:
        if not self.config.weapon_simulation_enabled:
            return []
        events: List[WeaponEvent] = []
        now = datetime.now(timezone.utc)
        types = ["knife", "gun"]
        for idx, person_event in enumerate(person_events):
            if random.random() > self.config.weapon_simulation_rate:
                continue
            weapon_type = types[idx % 2]
            risk = RiskLevel.CRITICAL if weapon_type == "gun" else RiskLevel.HIGH
            events.append(
                WeaponEvent(
                    event_type="weapon",
                    confidence=person_event.confidence,
                    timestamp=now,
                    bbox=person_event.bbox,
                    weapon_type=weapon_type,
                    risk_level=risk,
                    metadata={"source_event": "person"},
                )
            )
        return events
