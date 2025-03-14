import asyncio
import json
import websockets
import threading

WS = "ws://192.168.100.191:8765"

async def receive_traffic_state(socketio):
    while True:
        try:
            async with websockets.connect(WS) as ws:
                while True:
                    message = await ws.recv()
                    traffic_state = json.loads(message)
                    print("📥 Dữ liệu nhận từ ESP32:", traffic_state)

                    if all(key in traffic_state for key in ["north_south", "east_west", "countdown"]):
                        payload = {
                            "north_south": traffic_state["north_south"],
                            "east_west": traffic_state["east_west"],
                            "countdown": traffic_state["countdown"],
                        }
                        socketio.emit("update_traffic", payload)
                        print("📩 Gửi trạng thái đèn:", payload)
        except Exception as e:
            print("⚠️ Lỗi WebSocket:", e)
            await asyncio.sleep(2)
