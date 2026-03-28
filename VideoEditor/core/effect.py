"""Effect module.

Provides a minimal effect model that can be applied to frames.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class Effect:
    """Represents a timeline effect with configurable intensity."""

    type: str
    intensity: float
    start_time: int
    duration: int

    def __post_init__(self) -> None:
        """Validate effect fields after initialization."""
        if not isinstance(self.type, str) or not self.type:
            raise ValueError("type must be a non-empty string")
        if not isinstance(self.intensity, (int, float)) or self.intensity < 0:
            raise ValueError("intensity must be a non-negative number")
        if not isinstance(self.start_time, int) or self.start_time < 0:
            raise ValueError("start_time must be a non-negative integer")
        if not isinstance(self.duration, int) or self.duration <= 0:
            raise ValueError("duration must be a positive integer")

    @property
    def end_time(self) -> int:
        """Return the end time of the effect."""
        return self.start_time + self.duration

    def is_active(self, t: int) -> bool:
        """Return True when the effect is active at time t."""
        return self.start_time <= t < self.end_time

    def apply(self, frame: Any) -> Any:
        """Apply the effect to a frame.

        This placeholder visualizes the effect for debugging.
        """
        # DEBUG ONLY
        return f"{frame}|EFFECT({self.type})"
