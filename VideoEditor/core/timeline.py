"""Timeline module.

Defines the Timeline placeholder used to organize clips and tracks in the editor.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .clip import Clip
from .track import Track
from .transform import Transform


@dataclass
class Timeline:
    """Coordinate tracks and clip placement across the full timeline.

    Purpose:
    - Own the ordered set of tracks and global clip placement operations.

    Inputs:
    - tracks: Optional initial track list.

    Outputs:
    - add_track()/add_clip()/remove_clip()/move_clip() mutate timeline state.
    - get_clips_at_time() and total_duration provide read accessors.
    """

    tracks: List[Track] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate timeline initialization inputs.

        Inputs:
        - tracks field on this instance.

        Output:
        - None. Raises when values are invalid.
        """
        for track in self.tracks:
            if not isinstance(track, Track):
                raise TypeError("tracks must contain Track instances")

    @property
    def total_duration(self) -> int:
        """Return the maximum clip end time across all tracks.

        Inputs:
        - Current timeline tracks and clips.

        Output:
        - Integer duration ending at the furthest clip end.
        """
        max_end = 0
        for track in self.tracks:
            for clip in track.clips:
                if clip.end_time > max_end:
                    max_end = clip.end_time
        return max_end

    def add_track(self) -> Track:
        """Create and append a new uniquely named track.

        Inputs:
        - None.

        Output:
        - Newly created Track instance.
        """
        next_index = 1
        existing_ids = {track.id for track in self.tracks}
        while f"track_{next_index}" in existing_ids:
            next_index += 1

        track = Track(id=f"track_{next_index}")
        self.tracks.append(track)
        return track

    def add_clip(self, clip: Clip, track_id: str, start_time: int) -> None:
        """Place clip on the target track at start_time.

        Inputs:
        - clip: Clip to place.
        - track_id: Destination track identifier.
        - start_time: New clip start time.

        Output:
        - None. Mutates clip start time and track clip list.
        """
        if not isinstance(clip, Clip):
            raise TypeError("clip must be a Clip instance")
        if not isinstance(start_time, int) or start_time < 0:
            raise ValueError("start_time must be a non-negative integer")

        track = self._get_track(track_id)
        original_start = clip.start_time
        clip.start_time = start_time

        try:
            track.add_clip(clip)
        except Exception:
            clip.start_time = original_start
            raise

    def remove_clip(self, clip_id: str) -> None:
        """Remove clip_id from the track that contains it.

        Inputs:
        - clip_id: Identifier of the clip to remove.

        Output:
        - None. Mutates track clip lists.
        """
        if not isinstance(clip_id, str) or not clip_id:
            raise ValueError("clip_id must be a non-empty string")

        for track in self.tracks:
            for clip in track.clips:
                if clip.id == clip_id:
                    track.remove_clip(clip_id)
                    return

        raise ValueError(f"clip with id '{clip_id}' was not found")

    def move_clip(self, clip_id: str, new_start_time: int, new_track_id: str) -> None:
        """Move an existing clip to a new start time and destination track.

        Inputs:
        - clip_id: Identifier of clip to move.
        - new_start_time: Destination start time.
        - new_track_id: Destination track identifier.

        Output:
        - None. Mutates clip timing and track membership.
        """
        if not isinstance(clip_id, str) or not clip_id:
            raise ValueError("clip_id must be a non-empty string")
        if not isinstance(new_start_time, int) or new_start_time < 0:
            raise ValueError("new_start_time must be a non-negative integer")

        source_track, clip = self._find_clip(clip_id)
        if source_track is None or clip is None:
            raise ValueError(f"clip with id '{clip_id}' was not found")

        destination_track = self._get_track(new_track_id)

        original_start = clip.start_time
        source_track.remove_clip(clip_id)
        clip.start_time = new_start_time

        try:
            destination_track.add_clip(clip)
        except Exception:
            clip.start_time = original_start
            source_track.add_clip(clip)
            raise

    def get_clips_at_time(self, t: int) -> List[Clip]:
        """Return clips active at timeline time t.

        Inputs:
        - t: Timeline time to query.

        Output:
        - List of active clips across all tracks.
        """
        if not isinstance(t, int) or t < 0:
            raise ValueError("t must be a non-negative integer")

        active_clips: List[Clip] = []
        for track in self.tracks:
            for clip in track.clips:
                if clip.start_time <= t < clip.end_time:
                    active_clips.append(clip)
        return active_clips

    def to_dict(self) -> dict:
        """Serialize timeline structure to a dictionary.

        Inputs:
        - None. Uses current timeline state.

        Output:
        - Dictionary containing tracks, clips, and transform metadata.
        """
        tracks_data = []
        for track in self.tracks:
            clips_data = []
            for clip in track.clips:
                clip_dict = {
                    "id": clip.id,
                    "start_time": clip.start_time,
                    "duration": clip.duration,
                    "layer": clip.layer,
                    "transform": {
                        "x": clip.transform.x,
                        "y": clip.transform.y,
                        "scale": clip.transform.scale,
                        "rotation": clip.transform.rotation,
                    },
                }
                clips_data.append(clip_dict)
            
            tracks_data.append({
                "id": track.id,
                "clips": clips_data,
            })
        
        return {"tracks": tracks_data}

    @classmethod
    def from_dict(cls, data: dict) -> "Timeline":
        """Deserialize timeline structure from a dictionary.

        Inputs:
        - data: Dictionary with "tracks" key containing track/clip metadata.

        Output:
        - New Timeline instance with reconstructed tracks and clips.
        """
        timeline = cls()
        
        for track_data in data.get("tracks", []):
            track = Track(id=track_data["id"])
            
            for clip_data in track_data.get("clips", []):
                transform_data = clip_data.get("transform", {})
                transform = Transform(
                    x=transform_data.get("x", 0),
                    y=transform_data.get("y", 0),
                    scale=transform_data.get("scale", 1.0),
                    rotation=transform_data.get("rotation", 0.0),
                )
                
                clip = Clip(
                    id=clip_data["id"],
                    frames=[],
                    start_time=clip_data["start_time"],
                    duration=clip_data["duration"],
                    layer=clip_data["layer"],
                    transform=transform,
                )
                track.clips.append(clip)
            
            timeline.tracks.append(track)
        
        return timeline

    def _get_track(self, track_id: str) -> Track:
        """Look up a track by id.

        Inputs:
        - track_id: Track identifier.

        Output:
        - Matching Track instance.
        """
        if not isinstance(track_id, str) or not track_id:
            raise ValueError("track_id must be a non-empty string")

        for track in self.tracks:
            if track.id == track_id:
                return track
        raise ValueError(f"track with id '{track_id}' was not found")

    def _find_clip(self, clip_id: str) -> Tuple[Optional[Track], Optional[Clip]]:
        """Find a clip and its containing track.

        Inputs:
        - clip_id: Clip identifier.

        Output:
        - Tuple of (track, clip) or (None, None) when not found.
        """
        for track in self.tracks:
            for clip in track.clips:
                if clip.id == clip_id:
                    return track, clip
        return None, None
