import cv2
import numpy as np
import threading
from ultralytics import YOLO

# 🔹 Load mô hình YOLOv8 Segmentation
model = YOLO("yolov8m-seg.pt")

# 🔹 Danh sách Camera
CAMERA_URLS = [
    "http://192.168.100.150:81/stream",  # Đông - Tây
    "http://192.168.100.151:81/stream",  # Bắc - Nam
    "http://192.168.100.152:81/stream",  # Đông - Tây
    "http://192.168.100.153:81/stream",  # Bắc - Nam
]

# 🔹 Vùng ROI
ROI_POINTS = [
    np.array([(259, 91), (404, 92), (464, 226), (201, 216)], dtype=np.int32),
    np.array( [(207, 237), (369, 238), (437, 372), (153, 370)], dtype=np.int32),
    np.array([(166, 113), (317, 105), (381, 237), (119, 255)], dtype=np.int32),
    np.array( [(189, 229), (351, 224), (425, 359), (127, 372)], dtype=np.int32),
]

density_ns = 0.0
density_ew = 0.0
lock = threading.Lock()

def generate_frames(camera_url, camera_index):
    global density_ns, density_ew
    cap = cv2.VideoCapture(camera_url)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.resize(frame, (640, 480))
        roi_points = ROI_POINTS[camera_index]
        cv2.polylines(frame, [roi_points], isClosed=True, color=(0, 0, 255), thickness=2)

        results = model(frame, conf=0.4)[0]
        masks = results.masks
        names = results.names

        density = 0
        if masks is not None and len(masks) > 0:
            masks = masks.data.cpu().numpy()
            classes = results.boxes.cls.cpu().numpy()
            image_height, image_width = frame.shape[:2]

            roi_mask = np.zeros((image_height, image_width), dtype=np.uint8)
            cv2.fillPoly(roi_mask, [roi_points], 1)

            total_mask_area = 0
            overlay = frame.copy()

            for idx, mask in enumerate(masks):
                if names[int(classes[idx])] != "car":
                    continue

                mask_resized = cv2.resize(mask, (image_width, image_height), interpolation=cv2.INTER_NEAREST)
                mask_binary = (mask_resized > 0.5).astype(np.uint8)
                mask_in_roi = cv2.bitwise_and(mask_binary, roi_mask)
                total_mask_area += np.sum(mask_in_roi)

                total_roi_area = np.sum(roi_mask)
                density_percentage = (total_mask_area / total_roi_area) * 100 if total_roi_area > 0 else 0

                if density_percentage < 30:
                    color = (0, 255, 0)
                elif density_percentage < 60:
                    color = (0, 255, 255)
                else:
                    color = (0, 0, 255)

                colored_mask = np.zeros_like(frame, dtype=np.uint8)
                for c in range(3):
                    colored_mask[:, :, c] = mask_in_roi * color[c]

                overlay = cv2.addWeighted(overlay, 1, colored_mask, 0.5, 0)

            cv2.putText(overlay, f"Mat do xe: {density_percentage:.2f}%", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            frame = overlay

        with lock:
            if camera_index == 0:
                density_ns = density
            else:
                density_ew = density

        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
