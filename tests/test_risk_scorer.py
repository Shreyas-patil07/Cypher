from datetime import datetime, timezone

from cypher.detection import PersonEvent, RiskLevel, RiskScorer, WeaponEvent


def test_risk_scorer_assigns_levels():
    scorer = RiskScorer()
    ts = datetime.now(timezone.utc)

    person = PersonEvent(event_type="person", confidence=0.8, timestamp=ts, bbox=(0, 0, 1, 1))
    knife = WeaponEvent(
        event_type="weapon",
        confidence=0.8,
        timestamp=ts,
        bbox=(0, 0, 1, 1),
        weapon_type="knife",
    )
    gun = WeaponEvent(
        event_type="weapon",
        confidence=0.8,
        timestamp=ts,
        bbox=(0, 0, 1, 1),
        weapon_type="gun",
    )

    assert scorer.score(person) == RiskLevel.MEDIUM
    assert scorer.score(knife) == RiskLevel.HIGH
    assert scorer.score(gun) == RiskLevel.CRITICAL
    assert scorer.priority(RiskLevel.CRITICAL) > scorer.priority(RiskLevel.MEDIUM)
