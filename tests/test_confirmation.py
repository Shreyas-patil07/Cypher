from datetime import datetime, timezone

from cypher.detection import MultiFrameConfirmation, PersonEvent


def make_person(ts: datetime) -> PersonEvent:
    return PersonEvent(event_type="person", confidence=0.9, timestamp=ts, bbox=(0, 0, 1, 1))


def test_confirmation_triggers_on_threshold_and_resets():
    ts = datetime.now(timezone.utc)
    conf = MultiFrameConfirmation(thresholds={"person": 2})

    ev1 = make_person(ts)
    confirmed, counters = conf.update([ev1])
    assert confirmed == []
    assert counters["person"] == 1

    ev2 = make_person(ts)
    confirmed, counters = conf.update([ev2])
    assert len(confirmed) == 1
    assert counters["person"] == 0

    # No event next frame should keep counter at 0
    confirmed, counters = conf.update([])
    assert confirmed == []
    assert counters.get("person", 0) == 0
