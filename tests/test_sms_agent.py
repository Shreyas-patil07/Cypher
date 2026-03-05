from datetime import datetime, timezone

from cypher.alerts import AlertEvent, RateLimiter, RiskLevel, SMSAgent, SMSAgentConfig


class FakeMessagingClient:
    def __init__(self):
        self.sent = []

    def send_sms(self, *, body: str, recipients, sender_id=None):
        self.sent.append({"body": body, "recipients": list(recipients), "sender_id": sender_id})
        return "msg-1"


def make_event(risk=RiskLevel.HIGH) -> AlertEvent:
    return AlertEvent(
        event_id="evt-1",
        event_type="weapon",
        risk_level=risk,
        camera_id="Cam-1",
        timestamp=datetime.now(timezone.utc),
        confidence=0.9,
        metadata={},
    )


def test_sms_agent_sends_when_enabled_and_above_threshold():
    client = FakeMessagingClient()
    cfg = SMSAgentConfig(
        enabled=True,
        recipients=["+10000000000"],
        min_risk_level=RiskLevel.MEDIUM,
        rate_limit_per_hour=5,
    )
    agent = SMSAgent(config=cfg, messaging_client=client)

    records = agent.process_event(make_event(RiskLevel.HIGH))

    assert len(records) == 1
    assert records[0].status == "sent"
    assert client.sent[0]["recipients"] == ["+10000000000"]


def test_sms_agent_respects_rate_limit():
    client = FakeMessagingClient()
    cfg = SMSAgentConfig(
        enabled=True,
        recipients=["+10000000000"],
        min_risk_level=RiskLevel.MEDIUM,
        rate_limit_per_hour=1,
    )
    limiter = RateLimiter(max_per_hour=1)
    agent = SMSAgent(config=cfg, messaging_client=client, rate_limiter=limiter)

    first = agent.process_event(make_event(RiskLevel.HIGH))
    second = agent.process_event(make_event(RiskLevel.HIGH))

    assert len(first) == 1
    assert first[0].status == "sent"
    assert any(record.status == "skipped" for record in second)
