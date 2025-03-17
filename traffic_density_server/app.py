from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import threading
import asyncio
from camera import generate_frames, get_density_data
from traffic import calculate_traffic_lights
from websocket_client import send_traffic_data, receive_traffic_state

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Chạy nhận dữ liệu từ ESP32 trong luồng riêng
threading.Thread(
    target=lambda: asyncio.run(receive_traffic_state(socketio)), daemon=True
).start()


@app.route("/video_feed/<int:cam_id>")
def video_feed(cam_id):
    """Trả về luồng video từ camera"""
    return Response(
        generate_frames(cam_id), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/")
def index():
    """Trang chính hiển thị video"""
    return render_template("index.html")


if __name__ == "__main__":
    threading.Thread(
        target=lambda: asyncio.run(send_traffic_data()), daemon=True
    ).start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
