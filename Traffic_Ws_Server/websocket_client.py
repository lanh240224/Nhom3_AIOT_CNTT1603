import asyncio
import websockets
import json
from traffic import traffic_state, broadcast_state, update_timings
from colorama import Fore, Style

connected_clients = set()

async def receive_commands(websocket):
    """Nhận và xử lý lệnh từ Server"""
    try:
        async for message in websocket:
            print(Fore.GREEN + Style.BRIGHT + f"📩 Nhận dữ liệu từ Server: {message}" + Style.RESET_ALL)    

            try:
                data = json.loads(message)
                update_timings(data)
                await broadcast_state(connected_clients)
            except json.JSONDecodeError:
                print("⚠️ Lỗi: Dữ liệu không hợp lệ!", message)
    except websockets.exceptions.ConnectionClosedError:
        print("⚠️ Server đã đóng kết nối.")

async def handle_client(websocket):
    """Xử lý kết nối từ ESP32"""
    global connected_clients
    connected_clients.add(websocket)
    print(f"🔗 ESP32 kết nối! Hiện có {len(connected_clients)} thiết bị.")

    try:
        await websocket.send(json.dumps(traffic_state))
        await receive_commands(websocket)
    except websockets.exceptions.ConnectionClosedError:
        print("⚠️ ESP32 ngắt kết nối.")
    finally:
        connected_clients.remove(websocket)

async def websocket_server():
    """Chạy WebSocket Server"""
    server = await websockets.serve(handle_client, "0.0.0.0", 8765)
    print("🚀 WebSocket server đang chạy trên cổng 8765")
    await server.wait_closed()
