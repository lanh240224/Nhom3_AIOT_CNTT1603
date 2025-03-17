import cv2
import numpy as np
from ultralytics import YOLO
import threading

CAMERA_URLS = [
    "http://192.168.100.150:81/stream",
    "http://192.168.100.151:81/stream",
    "http://192.168.100.152:81/stream",
    "http://192.168.100.153:81/stream",
]

ROI_POINTS = [
    np.array([(339, 210), (521, 216), (596, 380), (265, 370)], dtype=np.int32),
    np.array([(298, 292), (497, 296), (573, 474), (216, 449)], dtype=np.int32),
    np.array([(203, 177), (384, 168), (466, 324), (133, 342)], dtype=np.int32),
    np.array([(249, 304), (445, 295), (537, 482), (173, 490)], dtype=np.int32),
]

model = YOLO("yolov8m-seg.pt")
lock = threading.Lock()
density_ns, density_ew = 0.0, 0.0


def generate_frames(camera_index):
    """Xử lý hình ảnh từ camera và tính mật độ xe"""
    global density_ns, density_ew
    cap = cv2.VideoCapture(CAMERA_URLS[camera_index])

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.resize(frame, (800, 600))
        roi_points = ROI_POINTS[camera_index]
        cv2.polylines(
            frame, [roi_points], isClosed=True, color=(0, 0, 255), thickness=2
        )

        results = model(frame, conf=0.4)[0]
        masks = results.masks
        density = 0

        if masks is not None:
            total_mask_area = 0
            roi_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            cv2.fillPoly(roi_mask, [roi_points], 1)

            for mask in masks.data.cpu().numpy():
                mask_resized = cv2.resize(
                    mask,
                    (frame.shape[1], frame.shape[0]),
                    interpolation=cv2.INTER_NEAREST,
                )
                mask_binary = (mask_resized > 0.5).astype(np.uint8)
                mask_in_roi = cv2.bitwise_and(mask_binary, roi_mask)
                total_mask_area += np.sum(mask_in_roi)

            total_roi_area = np.sum(roi_mask)
            density = (
                (total_mask_area / total_roi_area) * 100 if total_roi_area > 0 else 0
            )

        with lock:
            if camera_index in [0, 1]:  # Bắc - Nam
                density_ns = density
            else:  # Đông - Tây
                density_ew = density

        _, buffer = cv2.imencode(".jpg", frame)
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"


def get_density_data():
    """Trả về mật độ xe Bắc-Nam và Đông-Tây"""
    with lock:
        return density_ns, density_ew
