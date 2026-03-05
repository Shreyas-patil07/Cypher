from ultralytics import YOLO
import cv2
import numpy as np

from video_utils import prepare_video_io, preview_and_save

# Path to the trained segmentation model
MODEL_PATH = 'car_damage_detection_model.pt'  # segmentation-only model
OUTPUT_DIR = 'video_results'
VIDEO_PATH = 'car damage video.mp4'  # Set your video path here

# Class names and colors (from dataset/data.yaml)
CLASS_NAMES = ['Car-Damage']
CLASS_COLORS = [(255, 255, 0)]  # fire: red, smoke: blue (BGR for OpenCV)

model = YOLO(MODEL_PATH)

cap, out, output_path, width, height, fps = prepare_video_io(
    VIDEO_PATH,
    OUTPUT_DIR,
    output_name='annotated_video.mp4',
    fallback_size=(1920, 1080),
    fallback_fps=25,
)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    # Run segmentation inference on the frame
    results = model(frame, verbose=False)
    r = results[0]
    annotated_frame = frame.copy()
    if hasattr(r, 'masks') and r.masks is not None:
        masks = r.masks.data.cpu().numpy()  # shape: (num_instances, H, W)
        classes = r.boxes.cls.cpu().numpy().astype(int)  # class indices for each mask
        for mask, cls_idx in zip(masks, classes):
            color = CLASS_COLORS[cls_idx]
            mask = (mask > 0.5).astype(np.uint8)
            # Resize mask to match frame size
            mask_resized = cv2.resize(mask, (annotated_frame.shape[1], annotated_frame.shape[0]), interpolation=cv2.INTER_NEAREST)
            colored_mask = np.zeros_like(annotated_frame, dtype=np.uint8)
            for c in range(3):
                colored_mask[:, :, c] = mask_resized * color[c]
            annotated_frame = cv2.addWeighted(annotated_frame, 1.0, colored_mask, 0.5, 0)
            # Find centroid of the mask for label placement
            moments = cv2.moments(mask_resized)
            if moments["m00"] != 0:
                cx = int(moments["m10"] / moments["m00"])
                cy = int(moments["m01"] / moments["m00"])
                label = CLASS_NAMES[cls_idx]
                cv2.putText(
                    annotated_frame,
                    label,
                    (cx, cy),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 0),  # White text for contrast
                    2,
                    cv2.LINE_AA
                )
    preview_and_save(annotated_frame, out, preview_size=(1920, 1080))
    # Press 'q' to quit early
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print(f"Processed video: {VIDEO_PATH}\nAnnotated video saved at: {output_path}") 