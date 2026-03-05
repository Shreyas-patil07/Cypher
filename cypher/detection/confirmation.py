"""Multi-frame confirmation logic for stabilizing alerts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple

from .models import Event


@dataclass
class MultiFrameConfirmation:
    thresholds: Dict[str, int]
    counters: Dict[str, int] = field(default_factory=dict)

    def update(self, events: Iterable[Event]) -> Tuple[List[Event], Dict[str, int]]:
        """Update counters with current frame events and return confirmed ones.

        Returns a tuple of (confirmed_events, current_counters).
        """

        confirmed: List[Event] = []
        seen_types = {event.event_type for event in events}

        # Reset counters for event types not seen this frame.
        for event_type in list(self.counters.keys()):
            if event_type not in seen_types:
                self.counters[event_type] = 0

        # Increment counters for seen events and check thresholds.
        for event in events:
            threshold = self.thresholds.get(event.event_type, 1)
            self.counters[event.event_type] = self.counters.get(event.event_type, 0) + 1
            if self.counters[event.event_type] >= threshold:
                confirmed.append(event)
                self.counters[event.event_type] = 0

        return confirmed, dict(self.counters)
