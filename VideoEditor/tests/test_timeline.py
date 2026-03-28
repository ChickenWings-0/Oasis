"""Functional tests for timeline, track, and clip behavior."""

import os
import sys

try:
    from VideoEditor.core.clip import Clip
    from VideoEditor.core.effect import Effect
    from VideoEditor.core.renderer import Renderer
    from VideoEditor.core.text_overlay import TextOverlay
    from VideoEditor.core.timeline import Timeline
    from VideoEditor.core.transition import Transition
except ModuleNotFoundError:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from VideoEditor.core.clip import Clip
    from VideoEditor.core.effect import Effect
    from VideoEditor.core.renderer import Renderer
    from VideoEditor.core.text_overlay import TextOverlay
    from VideoEditor.core.timeline import Timeline
    from VideoEditor.core.transition import Transition


def assert_raises(error_type, func, *args, **kwargs):
    """Assert that calling func raises error_type."""
    try:
        func(*args, **kwargs)
    except error_type:
        return
    except Exception as exc:
        raise AssertionError(
            f"Expected {error_type.__name__}, got {type(exc).__name__}"
        ) from exc
    raise AssertionError(f"Expected {error_type.__name__} to be raised")


def test_basic_timeline_setup():
    """Create a timeline and verify a newly added track exists."""
    timeline = Timeline()
    track = timeline.add_track()

    assert track.id == "track_1"
    assert len(timeline.tracks) == 1
    assert timeline.tracks[0] is track


def test_add_clip():
    """Add a clip to a track and verify placement."""
    timeline = Timeline()
    track = timeline.add_track()
    clip = Clip(id="clip_1", frames=list(range(10)), start_time=0, duration=10, layer=0)

    timeline.add_clip(clip, track.id, 5)

    assert clip.start_time == 5
    assert len(track.clips) == 1
    assert track.clips[0] is clip


def test_move_clip_within_and_across_tracks():
    """Move a clip within the same track and then to a different track."""
    timeline = Timeline()
    track_1 = timeline.add_track()
    track_2 = timeline.add_track()

    clip = Clip(id="clip_move", frames=list(range(6)), start_time=0, duration=6, layer=0)
    timeline.add_clip(clip, track_1.id, 2)

    timeline.move_clip("clip_move", 12, track_1.id)
    assert clip.start_time == 12
    assert clip in track_1.clips

    timeline.move_clip("clip_move", 20, track_2.id)
    assert clip.start_time == 20
    assert clip not in track_1.clips
    assert clip in track_2.clips


def test_split_clip():
    """Split a clip and verify resulting durations and positions."""
    clip = Clip(id="clip_split", frames=list(range(10)), start_time=5, duration=10, layer=0)

    first, second = clip.split(4)

    assert first.start_time == 5
    assert first.duration == 4
    assert first.end_time == 9
    assert len(first.frames) == 4

    assert second.start_time == 9
    assert second.duration == 6
    assert second.end_time == 15
    assert len(second.frames) == 6


def test_trim_clip():
    """Trim a clip and verify updated start time and duration."""
    clip = Clip(id="clip_trim", frames=list(range(10)), start_time=3, duration=10, layer=0)

    clip.trim(start_offset=2, end_offset=3)

    assert clip.start_time == 5
    assert clip.duration == 5
    assert clip.end_time == 10
    assert clip.frames == [2, 3, 4, 5, 6]


def test_overlap_prevention():
    """Reject clip insertion when it overlaps another clip on the same track."""
    timeline = Timeline()
    track = timeline.add_track()

    clip_1 = Clip(id="clip_a", frames=[], start_time=0, duration=10, layer=0)
    clip_2 = Clip(id="clip_b", frames=[], start_time=0, duration=5, layer=0)

    timeline.add_clip(clip_1, track.id, 0)
    assert_raises(ValueError, timeline.add_clip, clip_2, track.id, 5)


def test_add_clip_rollback_on_failure():
    """Keep clip state unchanged when add_clip fails due to overlap."""
    timeline = Timeline()
    track = timeline.add_track()

    first_clip = Clip(id="clip_base", frames=[], start_time=0, duration=10, layer=0)
    second_clip = Clip(id="clip_overlap", frames=[], start_time=1, duration=4, layer=0)

    timeline.add_clip(first_clip, track.id, 0)

    original_start = second_clip.start_time
    assert_raises(ValueError, timeline.add_clip, second_clip, track.id, 5)

    assert first_clip.start_time == 0
    assert first_clip.duration == 10
    assert second_clip.start_time == original_start
    assert all(clip.id != second_clip.id for clip in track.clips)


def test_move_clip_rollback_on_failure():
    """Keep clip in original track and time when move fails due to overlap."""
    timeline = Timeline()
    source_track = timeline.add_track()
    destination_track = timeline.add_track()

    moving_clip = Clip(id="clip_move_fail", frames=[], start_time=0, duration=8, layer=0)
    blocking_clip = Clip(id="clip_block", frames=[], start_time=0, duration=10, layer=0)

    timeline.add_clip(moving_clip, source_track.id, 2)
    timeline.add_clip(blocking_clip, destination_track.id, 5)

    original_start = moving_clip.start_time
    assert_raises(
        ValueError,
        timeline.move_clip,
        moving_clip.id,
        8,
        destination_track.id,
    )

    assert moving_clip in source_track.clips
    assert moving_clip not in destination_track.clips
    assert moving_clip.start_time == original_start


def test_get_clips_at_time():
    """Return all clips active at a specific timeline time."""
    timeline = Timeline()
    track_1 = timeline.add_track()
    track_2 = timeline.add_track()

    clip_1 = Clip(id="clip_t1", frames=[], start_time=0, duration=10, layer=0)
    clip_2 = Clip(id="clip_t2", frames=[], start_time=0, duration=5, layer=1)

    timeline.add_clip(clip_1, track_1.id, 0)
    timeline.add_clip(clip_2, track_2.id, 5)

    active = timeline.get_clips_at_time(6)
    active_ids = {clip.id for clip in active}

    assert active_ids == {"clip_t1", "clip_t2"}
    assert timeline.get_clips_at_time(11) == []


def test_renderer_pipeline_integration():
    """Run clip, transition, effect, and overlay pipeline without errors."""
    timeline = Timeline()
    track_1 = timeline.add_track()
    track_2 = timeline.add_track()

    clip_1 = Clip(id="clip_r1", frames=["a0", "a1", "a2"], start_time=0, duration=3, layer=0)
    clip_2 = Clip(id="clip_r2", frames=["b0", "b1", "b2"], start_time=0, duration=3, layer=1)
    timeline.add_clip(clip_1, track_1.id, 0)
    timeline.add_clip(clip_2, track_2.id, 0)

    transition = Transition(start_time=0, duration=3, type="fade")
    effect = Effect(type="brightness", intensity=0.5, start_time=0, duration=3)
    overlay = TextOverlay(text="hello", start_time=0, duration=3, x=10, y=20)

    renderer = Renderer()
    output_frame = renderer.render_frame(
        timeline,
        1,
        transitions=[transition],
        effects=[effect],
        overlays=[overlay],
    )

    assert output_frame is not None


def test_total_duration():
    """Compute total duration as the maximum clip end time."""
    timeline = Timeline()
    track_1 = timeline.add_track()
    track_2 = timeline.add_track()

    clip_1 = Clip(id="clip_d1", frames=[], start_time=0, duration=8, layer=0)
    clip_2 = Clip(id="clip_d2", frames=[], start_time=0, duration=5, layer=1)

    timeline.add_clip(clip_1, track_1.id, 0)
    timeline.add_clip(clip_2, track_2.id, 10)

    assert timeline.total_duration == 15


if __name__ == "__main__":
    test_basic_timeline_setup()
    test_add_clip()
    test_move_clip_within_and_across_tracks()
    test_split_clip()
    test_trim_clip()
    test_overlap_prevention()
    test_add_clip_rollback_on_failure()
    test_move_clip_rollback_on_failure()
    test_get_clips_at_time()
    test_renderer_pipeline_integration()
    test_total_duration()
    print("All timeline tests passed.")
