"""Renderer module.

Provides a minimal frame renderer for timeline-based clip playback.
"""

from typing import Any, List, Optional

from .effect import Effect
from .text_overlay import TextOverlay
from .timeline import Timeline
from .transition import Transition


class Renderer:
    """Resolve a timeline time into a rendered frame.

    Purpose:
    - Execute the core render pipeline used by higher-level interfaces.

    Inputs:
    - timeline: Source timeline containing tracks and clips.
    - t: Timeline time to evaluate.
    - transitions: Optional active transition definitions.
    - effects: Optional active effect definitions.
    - overlays: Optional active text overlays.

    Output:
    - The final rendered frame object for time t, or None when no clip is active.
    """

    def render_frame(
        self,
        timeline: Timeline,
        t: int,
        transitions: Optional[List[Transition]] = None,
        effects: Optional[List[Effect]] = None,
        overlays: Optional[List[TextOverlay]] = None,
    ) -> Any:
        """Render and return a single frame reference at time t.

        Pipeline:
        1. Get active clips from timeline.get_clips_at_time(t).
        2. Sort active clips by layer ascending.
        3. Resolve each clip's local frame index.
        4. Apply active transitions, effects, and overlays.
        5. Return the final top-most composited frame.
        """
        active_clips = timeline.get_clips_at_time(t)
        if not active_clips:
            return None

        active_clips = sorted(active_clips, key=lambda clip: clip.layer)

        top_frame = None
        resolved_frames: List[Any] = []
        for clip in active_clips:
            frame_index = t - clip.start_time
            if isinstance(clip.frames, list):
                if 0 <= frame_index < len(clip.frames):
                    source_frame = clip.frames[frame_index]
                    if source_frame is not None:
                        processed_frame = clip.transform.apply(source_frame, t)
                        resolved_frames.append(processed_frame)
                        top_frame = processed_frame
            else:
                source_frame = clip.frames
                if source_frame is not None:
                    processed_frame = clip.transform.apply(source_frame, t)
                    resolved_frames.append(processed_frame)
                    top_frame = processed_frame

        frame = top_frame

        if transitions:
            if len(resolved_frames) >= 2:
                frame_a = resolved_frames[-2]
                frame_b = resolved_frames[-1]
                for transition in transitions:
                    if transition.is_active(t):
                        frame = transition.apply(frame_a, frame_b, t)
                        break

        if effects:
            for effect in effects:
                if effect.is_active(t):
                    frame = effect.apply(frame)

        if overlays:
            for overlay in overlays:
                if overlay.is_active(t):
                    frame = overlay.render(frame)

        return frame
