import asyncio
import websockets
import json

WS = "ws://192.168.100.191:8765"


async def send_traffic_data():
    """Gửi dữ liệu thời gian đèn tín hiệu đến ESP32"""
    while True:
        density_ns, density_ew = get_density_data()
        green_ns = int(10 + 30 * (1 - density_ns))
        green_ew = int(10 + 30 * (1 - density_ew))
        red_ns = green_ew + 5
        red_ew = green_ns + 5

        payload = {"red": max(red_ns, 5), "green": max(green_ns, 5), "yellow": 5}

        try:
            async with websockets.connect(WS) as ws:
                await ws.send(json.dumps(payload))
                print("📤 Gửi dữ liệu đến ESP32:", payload)
        except Exception as e:
            print("⚠️ Lỗi WebSocket:", e)

        await asyncio.sleep(1)


async def receive_traffic_state(socketio):
    """Nhận dữ liệu trạng thái đèn từ ESP32"""
    while True:
        try:
            async with websockets.connect(WS) as ws:
                while True:
                    message = await ws.recv()
                    traffic_state = json.loads(message)

                    # Kiểm tra dữ liệu hợp lệ
                    if all(
                        k in traffic_state
                        for k in ["north_south", "east_west", "countdown"]
                    ):
                        density_red = (
                            get_density_data()[0]
                            if traffic_state["north_south"] == "red"
                            else get_density_data()[1]
                        )
                        payload = {
                            "north_south": traffic_state["north_south"],
                            "east_west": traffic_state["east_west"],
                            "density_red": density_red,
                            "countdown": traffic_state["countdown"],
                        }
                        socketio.emit("update_traffic", payload)
                        print("📩 Gửi trạng thái đèn:", payload)
                    else:
                        print("⚠️ Dữ liệu không hợp lệ:", traffic_state)

        except Exception as e:
            print("⚠️ Lỗi WebSocket:", e)
            await asyncio.sleep(2)
