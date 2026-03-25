from PIL import Image


def apply_camera_motion(frame, frame_index, total_frames, motion_type="none"):
    width, height = frame.size

    if motion_type == "zoom_in":
        scale = 1 + (frame_index / total_frames) * 0.1
    elif motion_type == "zoom_out":
        scale = 1.2 - (frame_index / total_frames) * 0.2
    else:
        scale = 1.0

    new_w = int(width * scale)
    new_h = int(height * scale)

    resized = frame.resize((new_w, new_h), Image.LANCZOS)

    # center crop
    left = (new_w - width) // 2
    top = (new_h - height) // 2

    cropped = resized.crop((left, top, left + width, top + height))

    # pan effect (safe implementation)
    if motion_type == "pan_left":
        shift = int((frame_index / total_frames) * 30)
        padded = Image.new("RGB", (width + shift, height))
        padded.paste(cropped, (shift, 0))
        cropped = padded.crop((0, 0, width, height))
    elif motion_type == "pan_right":
        shift = int((frame_index / total_frames) * 30)
        padded = Image.new("RGB", (width + shift, height))
        padded.paste(cropped, (0, 0))
        cropped = padded.crop((shift, 0, shift + width, height))

    return cropped
