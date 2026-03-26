from PIL import Image


def apply_camera_motion(frame, frame_index, total_frames, motion_type="none"):
    width, height = frame.size

    if motion_type == "zoom_in":
        scale = 1.0 + (frame_index / total_frames) * 0.20
    elif motion_type == "zoom_out":
        scale = 1.05 - (frame_index / total_frames) * 0.05
    else:
        scale = 1.0

    new_w = int(width * scale)
    new_h = int(height * scale)

    resized = frame.resize((new_w, new_h), Image.LANCZOS)

    # center crop
    left = (new_w - width) // 2
    top = (new_h - height) // 2

    cropped = resized.crop((left, top, left + width, top + height))

    return cropped
