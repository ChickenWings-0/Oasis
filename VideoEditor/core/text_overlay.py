"""TextOverlay module.

Provides a text overlay model for timeline-based text placement.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class TextOverlay:
    """Represents a text overlay positioned on the timeline."""

    text: str
    start_time: int
    duration: int
    x: int
    y: int

    def __post_init__(self) -> None:
        """Validate text overlay fields after initialization."""
        if not isinstance(self.text, str) or not self.text:
            raise ValueError("text must be a non-empty string")
        if not isinstance(self.start_time, int) or self.start_time < 0:
            raise ValueError("start_time must be a non-negative integer")
        if not isinstance(self.duration, int) or self.duration <= 0:
            raise ValueError("duration must be a positive integer")
        if not isinstance(self.x, int):
            raise TypeError("x must be an integer")
        if not isinstance(self.y, int):
            raise TypeError("y must be an integer")

    @property
    def end_time(self) -> int:
        """Return the end time of the text overlay."""
        return self.start_time + self.duration

    def is_active(self, t: int) -> bool:
        """Return True if the overlay is active at time t."""
        return self.start_time <= t < self.end_time

    def render(self, frame: Any) -> Any:
        """Render the text overlay on a frame.

        This placeholder visualizes the overlay for debugging.
        """
        # DEBUG ONLY
        return f"{frame}|TEXT({self.text})"
