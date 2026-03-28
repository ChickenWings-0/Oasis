from core.models import CameraTransform
import math


def ease_in_out(t: float) -> float:
    return t * t * (3 - 2 * t)


def static_motion(frame_idx, total_frames):
    t = frame_idx / (total_frames - 1) if total_frames > 1 else 0
    return CameraTransform(
        translate_x=0.0,
        translate_y=0.0,
        scale=1.0,
        rotate=0.0,
    )


def pan_right(frame_idx, total_frames):
    t = frame_idx / (total_frames - 1) if total_frames > 1 else 0
    t = ease_in_out(t)
    return CameraTransform(
        translate_x=0.1 * t,
        translate_y=0.0,
        scale=1.0,
        rotate=0.0,
    )


def pan_left(frame_idx, total_frames):
    t = frame_idx / (total_frames - 1) if total_frames > 1 else 0
    t = ease_in_out(t)
    return CameraTransform(
        translate_x=-0.1 * t,
        translate_y=0.0,
        scale=1.0,
        rotate=0.0,
    )


def zoom_in(frame_idx, total_frames):
    t = frame_idx / (total_frames - 1) if total_frames > 1 else 0
    t = ease_in_out(t)
    return CameraTransform(
        translate_x=0.0,
        translate_y=0.0,
        scale=1.0 + (0.1 * t),
        rotate=0.0,
    )


def zoom_out(frame_idx, total_frames):
    t = frame_idx / (total_frames - 1) if total_frames > 1 else 0
    t = ease_in_out(t)
    return CameraTransform(
        translate_x=0.0,
        translate_y=0.0,
        scale=1.0 - (0.1 * t),
        rotate=0.0,
    )


def breathe(frame_idx, total_frames):
    t = frame_idx / (total_frames - 1) if total_frames > 1 else 0
    return CameraTransform(
        translate_x=0.0,
        translate_y=0.0,
        scale=1.0 + 0.02 * math.sin(t * 2 * math.pi),
        rotate=0.0,
    )


MOTION_FUNCTIONS = {
    "static": static_motion,
    "pan_right": pan_right,
    "pan_left": pan_left,
    "zoom_in": zoom_in,
    "zoom_out": zoom_out,
    "breathe": breathe,
}


def get_camera_transform(motion_type: str, frame_idx: int, total_frames: int) -> CameraTransform:
    motion_fn = MOTION_FUNCTIONS.get(motion_type, static_motion)
    return motion_fn(frame_idx, total_frames)
