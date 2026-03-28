"""Track module.

Defines the Track placeholder used to group clips on a timeline lane.
"""

from dataclasses import dataclass, field
from typing import List

from .clip import Clip


@dataclass
class Track:
    """Represent one timeline lane containing non-overlapping clips.

    Purpose:
    - Group clips in a lane while enforcing no overlap inside that lane.

    Inputs:
    - id: Track identifier.
    - clips: Optional initial clips for the track.

    Outputs:
    - add_clip()/remove_clip() mutate track membership.
    - get_clips() returns clips sorted by start time.
    """

    id: str
    clips: List[Clip] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate track initialization inputs.

        Inputs:
        - id and clips fields on this instance.

        Output:
        - None. Raises when values are invalid.
        """
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("id must be a non-empty string")

        for clip in self.clips:
            if not isinstance(clip, Clip):
                raise TypeError("clips must contain Clip instances")

        self.clips.sort(key=lambda clip: clip.start_time)
        for i in range(len(self.clips) - 1):
            current = self.clips[i]
            next_clip = self.clips[i + 1]
            overlaps = not (
                next_clip.end_time <= current.start_time
                or next_clip.start_time >= current.end_time
            )
            if overlaps:
                raise ValueError("initial clips contain overlaps")

    def add_clip(self, clip: Clip) -> None:
        """Add a clip when it does not overlap existing track clips.

        Inputs:
        - clip: Clip to insert.

        Output:
        - None. Mutates the clips list.
        """
        if not isinstance(clip, Clip):
            raise TypeError("clip must be a Clip instance")
        if not self._check_overlap(clip):
            raise ValueError("clip overlaps with an existing clip in the track")
        self.clips.append(clip)
        self.clips.sort(key=lambda existing: existing.start_time)

    def remove_clip(self, clip_id: str) -> None:
        """Remove the first clip matching clip_id.

        Inputs:
        - clip_id: Identifier of the clip to remove.

        Output:
        - None. Mutates the clips list.
        """
        if not isinstance(clip_id, str) or not clip_id:
            raise ValueError("clip_id must be a non-empty string")

        for index, clip in enumerate(self.clips):
            if clip.id == clip_id:
                del self.clips[index]
                return

        raise ValueError(f"clip with id '{clip_id}' was not found")

    def get_clips(self) -> List[Clip]:
        """Return clips sorted by start_time.

        Inputs:
        - None.

        Output:
        - New sorted list of clips.
        """
        return sorted(self.clips, key=lambda clip: clip.start_time)

    def _check_overlap(self, new_clip: Clip) -> bool:
        """Check whether new_clip can be inserted without overlap.

        Inputs:
        - new_clip: Candidate clip.

        Output:
        - True when no overlap is found, otherwise False.
        """
        for existing in self.clips:
            overlaps = not (
                new_clip.end_time <= existing.start_time
                or new_clip.start_time >= existing.end_time
            )
            if overlaps:
                return False
        return True
