"""Keyframe module.

Provides a minimal keyframe animation system with linear interpolation.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Union


KeyframeValue = Union[float, Tuple[float, ...]]


@dataclass
class Keyframe:
    """Represents a value at a specific timeline time."""

    time: int
    value: KeyframeValue

    def __post_init__(self) -> None:
        """Validate keyframe data after initialization."""
        if not isinstance(self.time, int) or self.time < 0:
            raise ValueError("time must be a non-negative integer")

        if isinstance(self.value, tuple):
            if not self.value:
                raise ValueError("tuple value must not be empty")
            if not all(isinstance(item, (int, float)) for item in self.value):
                raise ValueError("tuple value must contain only numbers")
        elif not isinstance(self.value, (int, float)):
            raise ValueError("value must be a number or tuple of numbers")


@dataclass
class KeyframeTrack:
    """Store and evaluate keyframes for time-based values.

    Purpose:
    - Provide sorted keyframe storage and interpolation lookup.

    Inputs:
    - keyframes: Optional initial list of Keyframe instances.

    Outputs:
    - add_keyframe() mutates keyframe ordering.
    - get_value(t) returns clamped/interpolated values.
    """

    keyframes: List[Keyframe] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate and normalize initial keyframe inputs.

        Inputs:
        - keyframes field on this instance.

        Output:
        - None. Raises when values are invalid.
        """
        for keyframe in self.keyframes:
            if not isinstance(keyframe, Keyframe):
                raise TypeError("keyframes must contain Keyframe instances")
        self.keyframes.sort(key=lambda keyframe: keyframe.time)

    def add_keyframe(self, keyframe: Keyframe) -> None:
        """Insert keyframe while preserving chronological order.

        Inputs:
        - keyframe: Keyframe to insert.

        Output:
        - None. Mutates keyframes list.
        """
        if not isinstance(keyframe, Keyframe):
            raise TypeError("keyframe must be a Keyframe instance")

        insert_index = len(self.keyframes)
        for index, existing in enumerate(self.keyframes):
            if keyframe.time < existing.time:
                insert_index = index
                break
        self.keyframes.insert(insert_index, keyframe)

    def get_value(self, t: int) -> KeyframeValue:
        """Return the interpolated keyframe value at time t.

        Inputs:
        - t: Timeline time to evaluate.

        Output:
        - Scalar or tuple value resolved from keyframe data.

        Behavior:
        - One keyframe: return that value.
        - Outside range: clamp to nearest endpoint value.
        - Between keyframes: linearly interpolate.
        """
        if not isinstance(t, int):
            raise TypeError("t must be an integer")
        if not self.keyframes:
            raise ValueError("keyframes cannot be empty")

        if len(self.keyframes) == 1:
            return self.keyframes[0].value

        if t <= self.keyframes[0].time:
            return self.keyframes[0].value
        if t >= self.keyframes[-1].time:
            return self.keyframes[-1].value

        left = self.keyframes[0]
        right = self.keyframes[-1]
        for index in range(len(self.keyframes) - 1):
            current = self.keyframes[index]
            nxt = self.keyframes[index + 1]
            if current.time <= t <= nxt.time:
                left = current
                right = nxt
                break

        if left.time == right.time:
            return right.value

        progress = (t - left.time) / (right.time - left.time)
        return self._interpolate(left.value, right.value, progress)

    def _interpolate(
        self,
        start_value: KeyframeValue,
        end_value: KeyframeValue,
        progress: float,
    ) -> KeyframeValue:
        """Linearly interpolate between two keyframe values.

        Inputs:
        - start_value: Left keyframe value.
        - end_value: Right keyframe value.
        - progress: Normalized interpolation amount in [0, 1].

        Output:
        - Interpolated value matching the input value type.
        """
        if isinstance(start_value, tuple) and isinstance(end_value, tuple):
            if len(start_value) != len(end_value):
                raise ValueError("tuple keyframe values must have the same length")
            return tuple(
                start + (end - start) * progress
                for start, end in zip(start_value, end_value)
            )

        if isinstance(start_value, (int, float)) and isinstance(end_value, (int, float)):
            return float(start_value) + (float(end_value) - float(start_value)) * progress

        raise ValueError("keyframe values must have matching types for interpolation")
