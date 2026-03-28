"""Clip module.

Defines the Clip placeholder used to represent media segments in the editor.
"""

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, List, Union

from .transform import Transform


@dataclass
class Clip:
    """Represent one media segment placed on the timeline.

    Purpose:
    - Bundle frame content with timing, layer, and transform metadata.

    Inputs:
    - id: Unique clip identifier.
    - frames: Frame payload as a list or a single frame object.
    - start_time: Clip start time on the timeline.
    - duration: Clip duration in timeline units.
    - layer: Layer index used for visual ordering.
    - transform: Transform metadata applied during rendering.

    Outputs:
    - end_time: Computed end time.
    - split(): Two clips split at the requested local time.
    - trim(): In-place trimmed clip timing and frame range.
    """

    id: str
    frames: Union[List[Any], Any]
    start_time: int
    duration: int
    layer: int
    transform: Transform = field(default_factory=Transform)

    def __post_init__(self) -> None:
        """Validate clip initialization inputs.

        Inputs:
        - Dataclass fields on this instance.

        Output:
        - None. Raises when values are invalid.
        """
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("id must be a non-empty string")
        if not isinstance(self.start_time, int) or self.start_time < 0:
            raise ValueError("start_time must be a non-negative integer")
        if not isinstance(self.duration, int) or self.duration <= 0:
            raise ValueError("duration must be a positive integer")
        if not isinstance(self.layer, int) or self.layer < 0:
            raise ValueError("layer must be a non-negative integer")

    @property
    def end_time(self) -> int:
        """Compute the clip end time.

        Inputs:
        - start_time and duration from the clip.

        Output:
        - Integer timeline end time.
        """
        return self.start_time + self.duration

    def split(self, split_time: int) -> tuple["Clip", "Clip"]:
        """Split the clip into two new clips at local split_time.

        Inputs:
        - split_time: Relative split offset within this clip.

        Output:
        - Tuple of (left_clip, right_clip).
        """
        if not isinstance(split_time, int):
            raise TypeError("split_time must be an integer")
        if split_time <= 0 or split_time >= self.duration:
            raise ValueError("split_time must be > 0 and < duration of the clip")

        first_frames, second_frames = self._split_frames(split_time)

        first_clip = Clip(
            id=f"{self.id}_a",
            frames=first_frames,
            start_time=self.start_time,
            duration=split_time,
            layer=self.layer,
            transform=deepcopy(self.transform),
        )
        second_clip = Clip(
            id=f"{self.id}_b",
            frames=second_frames,
            start_time=self.start_time + split_time,
            duration=self.duration - split_time,
            layer=self.layer,
            transform=deepcopy(self.transform),
        )
        return first_clip, second_clip

    def trim(self, start_offset: int, end_offset: int) -> None:
        """Trim clip time and frame range from both edges.

        Inputs:
        - start_offset: Amount to remove from clip start.
        - end_offset: Amount to remove from clip end.

        Output:
        - None. Mutates clip timing and frames in place.
        """
        if not isinstance(start_offset, int) or not isinstance(end_offset, int):
            raise TypeError("start_offset and end_offset must be integers")
        if start_offset < 0 or end_offset < 0:
            raise ValueError("start_offset and end_offset must be non-negative")

        new_duration = self.duration - start_offset - end_offset
        if new_duration <= 0:
            raise ValueError("trim offsets must leave a positive duration")

        self.start_time += start_offset
        self.duration = new_duration

        if isinstance(self.frames, list):
            if end_offset == 0:
                self.frames = self.frames[start_offset:]
            else:
                self.frames = self.frames[start_offset : len(self.frames) - end_offset]

    def _split_frames(self, split_time: int) -> tuple[Any, Any]:
        """Split frame payload for split().

        Inputs:
        - split_time: Relative index for list frame payloads.

        Output:
        - Tuple containing left and right frame payload segments.
        """
        if isinstance(self.frames, list):
            return self.frames[:split_time], self.frames[split_time:]
        return self.frames, self.frames
