"""Transform module.

Provides a minimal transform model for clip placement metadata.
"""

from dataclasses import dataclass
from typing import Any

from .keyframe import KeyframeTrack


@dataclass
class Transform:
    """Describe how a clip frame is spatially transformed.

    Purpose:
    - Hold transform attributes consumed by the renderer.

    Inputs:
    - x, y: Position offsets.
    - scale: Uniform scalar multiplier.
    - rotation: Rotation value in degrees.
    - x_track: Optional keyframe track for animating x over time.

    Output:
    - apply() returns a transformed frame representation.
    """

    x: int = 0
    y: int = 0
    scale: float = 1.0
    rotation: float = 0.0
    x_track: KeyframeTrack | None = None

    def __post_init__(self) -> None:
        """Validate transform fields after initialization."""
        if not isinstance(self.x, int):
            raise TypeError("x must be an integer")
        if not isinstance(self.y, int):
            raise TypeError("y must be an integer")
        if not isinstance(self.scale, (int, float)) or self.scale <= 0:
            raise ValueError("scale must be a positive number")
        if not isinstance(self.rotation, (int, float)):
            raise TypeError("rotation must be a number")

    def get_state(self, t: int) -> dict[str, Any]:
        """Return transform state at timeline time t.

        Inputs:
        - t: Timeline time.

        Output:
        - A dictionary containing current x, y, scale, and rotation values.
        """
        x_value: Any = self.x
        if self.x_track is not None:
            x_value = self.x_track.get_value(t)
            if isinstance(x_value, float) and x_value.is_integer():
                x_value = int(x_value)

        return {
            "x": x_value,
            "y": self.y,
            "scale": self.scale,
            "rotation": self.rotation,
        }

    def apply(self, frame: Any, t: int = 0) -> Any:
        """Apply transform data to a frame representation.

        Inputs:
        - frame: Source frame value.
        - t: Timeline time used for keyframed transform lookup.

        Output:
        - Debug frame string containing position state.
        """
        state = self.get_state(t)
        # DEBUG ONLY
        return f"{frame}|POS({state['x']})"
