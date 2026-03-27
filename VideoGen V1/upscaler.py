from PIL import Image


def upscale_frames(frames, target_size=(1920, 1080)):
    upscaled = []

    for i, frame in enumerate(frames):
        print(f"Upscaling frame {i+1}/{len(frames)}...")

        if not isinstance(frame, Image.Image):
            frame = Image.fromarray(frame)

        frame = frame.resize(target_size, Image.LANCZOS)
        upscaled.append(frame)

    return upscaled
