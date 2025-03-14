from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import threading
import asyncio

from camera import generate_frames, CAMERA_URLS
from traffic import send_traffic_data
from websocket_client import receive_traffic_state

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Chạy WebSocket Flask trong luồng riêng
threading.Thread(target=lambda: asyncio.run(receive_traffic_state(socketio)), daemon=True).start()

@app.route("/video_feed/<int:cam_id>")
def video_feed(cam_id):
    """Trả về luồng video"""
    if cam_id >= len(CAMERA_URLS):
        return "Camera không tồn tại!", 404
    return Response(
        generate_frames(CAMERA_URLS[cam_id], cam_id),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )

@app.route("/")
def index():
    """Trang chính hiển thị video"""
    return render_template("index.html", cameras=CAMERA_URLS)

if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(send_traffic_data()), daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
