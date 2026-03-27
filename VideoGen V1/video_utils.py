import cv2
import numpy as np
from PIL import Image


def smooth_frames(frames, alpha=0.7):
    smoothed = []

    prev = np.array(frames[0])
    smoothed.append(frames[0])

    for i in range(1, len(frames)):
        curr = np.array(frames[i])

        # optical flow (motion estimation)
        flow = cv2.calcOpticalFlowFarneback(
            cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY),
            cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY),
            None,
            0.5, 3, 15, 3, 5, 1.2, 0
        )

        h, w = flow.shape[:2]
        flow_map = np.dstack((flow[..., 0], flow[..., 1]))

        # warp previous frame to align with current
        grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
        map_x = (grid_x + flow_map[..., 0]).astype(np.float32)
        map_y = (grid_y + flow_map[..., 1]).astype(np.float32)

        warped_prev = cv2.remap(prev, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        motion_magnitude = np.linalg.norm(flow, axis=2)
        motion_mask = np.clip(motion_magnitude / 5.0, 0, 1)

        adaptive_alpha = alpha * (1 - motion_mask)

        blended = (
            curr * (1 - adaptive_alpha[..., None]) +
            warped_prev * adaptive_alpha[..., None]
        ).astype(np.uint8)

        smoothed.append(Image.fromarray(blended))
        prev = curr

    return smoothed
