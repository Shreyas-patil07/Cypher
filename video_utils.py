import os
import cv2


def prepare_video_io(video_path, output_dir, output_name='annotated_video.mp4', fallback_size=(1280, 720), fallback_fps=25):
    """Open video and prepare writer with safe fallbacks."""
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or fallback_size[0]
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or fallback_size[1]
    fps = cap.get(cv2.CAP_PROP_FPS) or fallback_fps

    annotated_dir = os.path.join(output_dir, 'annotated')
    os.makedirs(annotated_dir, exist_ok=True)
    output_path = os.path.join(annotated_dir, output_name)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    return cap, out, output_path, width, height, fps


def preview_and_save(frame, writer, preview_size=(1280, 720), window_name='Live Preview'):
    """Show a resized preview and write the original frame."""
    preview_frame = cv2.resize(frame, preview_size)
    cv2.imshow(window_name, preview_frame)
    writer.write(frame)
    return preview_frame
