import asyncio
import websockets
import json
from config import traffic_state, TIMINGS, DEFAULT_TIMINGS

connected_clients = set()
TIMEOUT = 10  # Thời gian chờ tối đa trước khi reset (giây)


async def broadcast_state():
    """Gửi trạng thái đèn đến tất cả ESP32 đang kết nối."""
    if connected_clients:
        message = json.dumps(traffic_state)
        await asyncio.gather(*(client.send(message) for client in connected_clients))
        # print(f"📤 Đã gửi trạng thái đèn: {message}")


async def reset_to_default():
    """Reset trạng thái về mặc định nếu không nhận được lệnh mới."""
    global traffic_state
    print("⏳ Không nhận được lệnh mới, reset về trạng thái mặc định.")
    traffic_state.update(DEFAULT_TIMINGS)  # Reset trạng thái
    traffic_state["countdown"] = TIMINGS[traffic_state["north_south"]]
    await broadcast_state()


async def receive_commands(websocket):
    """Nhận và xử lý lệnh từ Server."""
    from traffic import update_timings

    try:
        async for message in websocket:
            print(f"\033[1;32m📩 Nhận thời gian từ Server: {message}\033[0m")

            # Kiểm tra dữ liệu JSON hợp lệ
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                print("⚠️ Lỗi: Dữ liệu không hợp lệ!", message)
                continue

            # Kiểm tra dữ liệu đầy đủ
            required_keys = {"red", "green", "yellow"}
            if not required_keys.issubset(data.keys()):
                print(f"⚠️ Thiếu khóa trong dữ liệu: {required_keys - data.keys()}")
                continue

            # Nếu đèn đang chạy, không thay đổi ngay lập tức
            if traffic_state["countdown"] > 1:
                print("⏳ Đèn đang chạy, cập nhật thời gian cho chu kỳ tiếp theo.")
                TIMINGS.update({k: int(v) for k, v in data.items() if k in TIMINGS})
                continue


            # Cập nhật thời gian mới
            await update_timings({k: int(v) for k, v in data.items() if k in TIMINGS})
            traffic_state["countdown"] = TIMINGS[traffic_state["north_south"]]
            await broadcast_state()

    except websockets.exceptions.ConnectionClosedError:
        print("⚠️ Server đã đóng kết nối.")


async def handle_client(websocket):
    """Xử lý kết nối từ ESP32."""
    global connected_clients

    connected_clients.add(websocket)
    print(f"🔗 ESP32 kết nối! Số ESP32 đang online: {len(connected_clients)}")

    try:
        await websocket.send(json.dumps(traffic_state))
        await receive_commands(websocket)

    except websockets.exceptions.ConnectionClosedError:
        print("⚠️ ESP32 đã ngắt kết nối.")
    finally:
        connected_clients.remove(websocket)
