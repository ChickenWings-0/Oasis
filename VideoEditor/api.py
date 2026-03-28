"""Public API layer for frontend-to-backend interaction.

Frontend code should use this module instead of importing core modules directly.
"""

from typing import Any

from VideoEditor.core.clip import Clip
from VideoEditor.core.engine import VideoEngine
from VideoEditor.core.timeline import Timeline
from VideoEditor.core.transform import Transform

_ENGINE = VideoEngine()


def create_timeline() -> Timeline:
    """Create and return a new timeline instance."""
    return Timeline()


def add_clip(timeline: Timeline, clip_data: dict) -> None:
    """Add a clip to a timeline using clip_data payload."""
    if not isinstance(timeline, Timeline):
        raise TypeError("timeline must be a Timeline instance")

    transform_data = clip_data.get("transform", {})
    transform = Transform(
        x=transform_data.get("x", 0),
        y=transform_data.get("y", 0),
        scale=transform_data.get("scale", 1.0),
        rotation=transform_data.get("rotation", 0.0),
    )

    clip = Clip(
        id=clip_data["id"],
        frames=clip_data["frames"],
        start_time=clip_data.get("start_time", 0),
        duration=clip_data["duration"],
        layer=clip_data.get("layer", 0),
        transform=transform,
    )

    track_id = clip_data.get("track_id")
    if track_id is None:
        if not timeline.tracks:
            track_id = timeline.add_track().id
        else:
            track_id = timeline.tracks[0].id

    timeline.add_clip(clip, track_id, clip.start_time)


def update_clip(timeline: Timeline, clip_id: str, data: dict) -> None:
    """Update an existing clip using partial data payload."""
    if not isinstance(timeline, Timeline):
        raise TypeError("timeline must be a Timeline instance")

    source_track, clip = timeline._find_clip(clip_id)
    if source_track is None or clip is None:
        raise ValueError(f"clip with id '{clip_id}' was not found")

    new_start_time = data.get("start_time", clip.start_time)
    new_track_id = data.get("track_id", source_track.id)
    if new_start_time != clip.start_time or new_track_id != source_track.id:
        timeline.move_clip(clip_id, new_start_time, new_track_id)
        _, clip = timeline._find_clip(clip_id)
        if clip is None:
            raise ValueError(f"clip with id '{clip_id}' was not found")

    if "frames" in data:
        clip.frames = data["frames"]
    if "duration" in data:
        clip.duration = data["duration"]
    if "layer" in data:
        clip.layer = data["layer"]
    if "transform" in data:
        transform_data = data["transform"]
        clip.transform = Transform(
            x=transform_data.get("x", clip.transform.x),
            y=transform_data.get("y", clip.transform.y),
            scale=transform_data.get("scale", clip.transform.scale),
            rotation=transform_data.get("rotation", clip.transform.rotation),
        )


def render_frame(timeline: Timeline, t: int) -> Any:
    """Render one frame at time t using the shared VideoEngine instance."""
    return _ENGINE.render(timeline, t)
