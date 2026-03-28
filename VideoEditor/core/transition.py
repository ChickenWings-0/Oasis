"""Transition module.

Provides a minimal transition model between two clips.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class Transition:
    """Represents a transition segment between two clips."""

    start_time: int
    duration: int
    type: str

    def __post_init__(self) -> None:
        """Validate transition fields after initialization."""
        if not isinstance(self.start_time, int) or self.start_time < 0:
            raise ValueError("start_time must be a non-negative integer")
        if not isinstance(self.duration, int) or self.duration <= 0:
            raise ValueError("duration must be a positive integer")
        if not isinstance(self.type, str) or not self.type:
            raise ValueError("type must be a non-empty string")

    @property
    def end_time(self) -> int:
        """Return the end time of the transition."""
        return self.start_time + self.duration

    def is_active(self, t: int) -> bool:
        """Return True when the transition is active at time t."""
        return self.start_time <= t < self.end_time

    def apply(self, frame_a: Any, frame_b: Any, t: int) -> Any:
        """Apply the transition effect between two frames.

        This placeholder visualizes the transition for debugging.
        """
        # DEBUG ONLY
        return f"TRANSITION({frame_a}->{frame_b})"
