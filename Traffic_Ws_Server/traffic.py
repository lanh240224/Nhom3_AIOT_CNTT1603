import asyncio
import json
from config import TIMINGS, traffic_state
from websocket_client import broadcast_state  # Tránh import tuần hoàn

async def traffic_light():
    """Cập nhật trạng thái đèn giao thông và gửi dữ liệu."""
    states = ["red", "green", "yellow"]

    while True:
        for state in states:
            # Cập nhật trạng thái đèn
            if state == "red":
                traffic_state.update({
                    "north_south": "red",
                    "east_west": "green",
                    "countdown": TIMINGS["red"],
                })
            elif state == "green":
                traffic_state.update({
                    "north_south": "green",
                    "east_west": "red",
                    "countdown": TIMINGS["green"],
                })
            elif state == "yellow":
                traffic_state.update({
                    "north_south": "yellow",
                    "east_west": "yellow",
                    "countdown": TIMINGS["yellow"],
                })

            # Gửi trạng thái cập nhật
            await broadcast_state()

            # Đếm ngược thời gian
            for i in range(traffic_state["countdown"], 0, -1):
                traffic_state["countdown"] = i
                await broadcast_state()
                await asyncio.sleep(1)

async def update_timings(new_timings):
    """Cập nhật thời gian đèn theo dữ liệu từ Server."""
    global TIMINGS
    TIMINGS.update(new_timings)
