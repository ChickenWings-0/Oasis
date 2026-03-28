"""Test JSON serialization for Timeline."""

import json
from VideoEditor.core.timeline import Timeline
from VideoEditor.core.clip import Clip
from VideoEditor.core.transform import Transform


def test_timeline_serialization():
    """Test to_dict() and from_dict() round-trip."""
    # Create timeline with tracks and clips
    timeline = Timeline()
    track1 = timeline.add_track()
    
    clip1 = Clip(
        id="clip1",
        frames=["A0", "A1"],
        start_time=0,
        duration=2,
        layer=0,
        transform=Transform(x=10, y=20, scale=1.5, rotation=45.0),
    )
    
    clip2 = Clip(
        id="clip2",
        frames=["B0"],
        start_time=5,
        duration=1,
        layer=1,
        transform=Transform(x=50, y=100),
    )
    
    timeline.add_clip(clip1, track1.id, 0)
    timeline.add_clip(clip2, track1.id, 5)
    
    # Serialize to dict
    timeline_dict = timeline.to_dict()
    print("Serialized timeline:")
    print(json.dumps(timeline_dict, indent=2))
    
    # Deserialize from dict
    restored_timeline = Timeline.from_dict(timeline_dict)
    
    # Verify structure
    assert len(restored_timeline.tracks) == 1
    restored_track = restored_timeline.tracks[0]
    assert restored_track.id == track1.id
    assert len(restored_track.clips) == 2
    
    # Verify clip 1
    restored_clip1 = restored_track.clips[0]
    assert restored_clip1.id == "clip1"
    assert restored_clip1.start_time == 0
    assert restored_clip1.duration == 2
    assert restored_clip1.layer == 0
    assert restored_clip1.transform.x == 10
    assert restored_clip1.transform.y == 20
    assert restored_clip1.transform.scale == 1.5
    assert restored_clip1.transform.rotation == 45.0
    
    # Verify clip 2
    restored_clip2 = restored_track.clips[1]
    assert restored_clip2.id == "clip2"
    assert restored_clip2.start_time == 5
    assert restored_clip2.duration == 1
    assert restored_clip2.layer == 1
    assert restored_clip2.transform.x == 50
    assert restored_clip2.transform.y == 100
    
    print("\n✓ Timeline serialization test passed!")


if __name__ == "__main__":
    test_timeline_serialization()
