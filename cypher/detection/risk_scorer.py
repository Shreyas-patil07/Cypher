"""Risk scoring utilities."""

from __future__ import annotations

from enum import Enum

from .models import Event, RiskLevel, WeaponEvent


class RiskScorer:
    def score(self, event: Event) -> RiskLevel:
        if isinstance(event, WeaponEvent):
            if event.weapon_type == "gun":
                return RiskLevel.CRITICAL
            return RiskLevel.HIGH
        # Default person event risk
        return RiskLevel.MEDIUM

    def priority(self, risk: RiskLevel) -> int:
        ordering = {RiskLevel.CRITICAL: 3, RiskLevel.HIGH: 2, RiskLevel.MEDIUM: 1, RiskLevel.LOW: 0}
        return ordering.get(risk, 0)
