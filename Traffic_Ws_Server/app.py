import asyncio
from websocket_client import websocket_server, connected_clients
from traffic import traffic_light

async def main():
    """Khởi chạy WebSocket Server và hệ thống đèn giao thông"""
    await asyncio.gather(websocket_server(), traffic_light(connected_clients))

if __name__ == "__main__":
    asyncio.run(main())
