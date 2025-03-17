import asyncio
import websockets
from websocket_client import handle_client
from traffic import traffic_light

async def main():
    server = await websockets.serve(handle_client, "0.0.0.0", 8765)
    print("🚀 WebSocket server đang chạy trên cổng 8765")

    # Chạy song song server và traffic_light
    await asyncio.gather(server.wait_closed(), traffic_light())

if __name__ == "__main__":
    asyncio.run(main())
