"""
Simple test runner for video editor pipeline.
Tests timeline, clips, transitions, effects, and overlays together.
"""

import sys
sys.path.insert(0, 'VideoEditor')

from core.timeline import Timeline
from core.clip import Clip
from core.transform import Transform
from core.renderer import Renderer
from core.transition import Transition
from core.effect import Effect
from core.text_overlay import TextOverlay
from VideoEditor.core.keyframe import Keyframe, KeyframeTrack


def main():
    print("=== Video Editor Pipeline Test ===\n")
    
    # Create timeline
    timeline = Timeline()
    
    # Create two tracks for overlapping clips
    track1 = timeline.add_track()
    track2 = timeline.add_track()
    
    # Create clips with simple frame data
    clip1 = Clip(
        id="clip1",
        frames=["A0", "A1", "A2"],
        start_time=0,
        duration=3,
        layer=0,
        transform=Transform()
    )
    
    # clip2 = Clip(
    #     id="clip2",
    #     frames=["B0", "B1", "B2"],
    #     start_time=2,
    #     duration=3,
    #     layer=1,
    #     transform=Transform()
    # )

    # Animate clip1 x position with keyframes (debug visualization)
    x_track = KeyframeTrack()
    x_track.add_keyframe(Keyframe(time=0, value=0))
    x_track.add_keyframe(Keyframe(time=2, value=100))
    clip1.transform.x_track = x_track
    
    # Add clips to separate tracks (allows overlap)
    timeline.add_clip(clip1, track1.id, 0)
    # timeline.add_clip(clip2, track2.id, 1)
    
    # Create transition, effect, text overlay
    transition = Transition(start_time=2, duration=1, type="fade")
    effect = Effect(type="brightness", intensity=0.5, start_time=0, duration=5)
    overlay = TextOverlay(text="Test Overlay", start_time=1, duration=3, x=10, y=10)
    
    # Create renderer
    renderer = Renderer()
    
    # Loop through time and render frames
    print("Rendering frames for t=0 to t=4:\n")
    for t in range(5):
        frame = renderer.render_frame(
            timeline,
            t,
            transitions=[transition],
            effects=[effect],
            overlays=[overlay],
        )
        print(f"t={t} → {frame}")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()
