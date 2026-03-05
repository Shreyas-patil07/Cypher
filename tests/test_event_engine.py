from datetime import datetime, timezone

from cypher.detection import Detection, EventConfig, EventDetectionEngine, RiskLevel


def test_detect_person_filters_by_class_and_confidence():
    detections = [
        Detection(bbox=(0, 0, 1, 1), confidence=0.8, class_id=0, class_name="person"),
        Detection(bbox=(0, 0, 1, 1), confidence=0.6, class_id=0, class_name="person"),
        Detection(bbox=(0, 0, 1, 1), confidence=0.9, class_id=2, class_name="car"),
    ]
    engine = EventDetectionEngine(
        EventConfig(
            person_confidence_threshold=0.7,
            person_confirmation_frames=3,
            weapon_simulation_enabled=False,
            weapon_simulation_rate=0.0,
        )
    )

    events = engine.detect_person(detections)

    assert len(events) == 1
    assert events[0].confidence == 0.8
    assert events[0].risk_level == RiskLevel.MEDIUM


def test_detect_weapon_simulated_alternates_and_sets_risk(monkeypatch):
    detections = [
        Detection(bbox=(0, 0, 1, 1), confidence=0.9, class_id=0, class_name="person"),
        Detection(bbox=(1, 1, 2, 2), confidence=0.95, class_id=0, class_name="person"),
    ]
    engine = EventDetectionEngine(
        EventConfig(
            person_confidence_threshold=0.5,
            person_confirmation_frames=1,
            weapon_simulation_enabled=True,
            weapon_simulation_rate=1.0,  # force simulation
        )
    )
    # Ensure random.random returns 0.0 so every person is simulated as a weapon.
    monkeypatch.setattr("random.random", lambda: 0.0)

    persons = engine.detect_person(detections)
    weapons = engine.detect_weapon_simulated(persons)

    assert len(weapons) == 2
    assert weapons[0].weapon_type == "knife"
    assert weapons[0].risk_level == RiskLevel.HIGH
    assert weapons[1].weapon_type == "gun"
    assert weapons[1].risk_level == RiskLevel.CRITICAL
