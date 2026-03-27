import cv2
import numpy as np
from PIL import Image


def smooth_frames(frames, alpha=0.7):
    if not frames:
        return []

    smoothed = [frames[0]]

    prev = np.array(frames[0]).astype(np.float32)

    for i in range(1, len(frames)):
        curr = np.array(frames[i]).astype(np.float32)

        # weighted blend with previous frame
        blended = cv2.addWeighted(curr, alpha, prev, 1 - alpha, 0)

        smoothed.append(Image.fromarray(blended.astype(np.uint8)))

        prev = blended

    return smoothed


def interpolate_frames(frames, factor=2):
    if not frames:
        return []

    if factor <= 1:
        return frames

    interpolated = []

    for i in range(len(frames) - 1):
        interpolated.append(frames[i])

        f1 = np.array(frames[i]).astype(np.float32)
        f2 = np.array(frames[i + 1]).astype(np.float32)

        for j in range(1, factor):
            t = j / factor
            mid = (1 - t) * f1 + t * f2
            interpolated.append(Image.fromarray(mid.astype(np.uint8)))

    interpolated.append(frames[-1])

    return interpolated


def frames_to_video(frames, output_path, fps=12):
    if not frames:
        return

    output_path = output_path.replace(".mp4", ".avi")

    frame_array = [np.array(f) for f in frames]
    height, width = frame_array[0].shape[:2]

    out = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"XVID"),
        fps,
        (width, height)
    )

    if not out.isOpened():
        raise RuntimeError("VideoWriter failed to open. Check codec support.")

    for frame in frame_array:
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame_bgr)

    out.release()
