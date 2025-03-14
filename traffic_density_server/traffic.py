import asyncio
import json
import websockets
import threading
from colorama import Fore, Style

WS = "ws://192.168.100.191:8765"
density_ns = 0.0
density_ew = 0.0
lock = threading.Lock()

async def send_traffic_data():
    while True:
        with lock:
            # Kiểm tra mật độ xe theo hướng đang có đèn đỏ
            if density_ns < 0.3 and density_ew < 0.3:
                # Nếu cả hai hướng có mật độ < 30%, không thay đổi đèn
                green_ns = 30
                green_ew = 30
            else:
                # Nếu một trong hai hướng có mật độ > 30%, tính lại thời gian
                green_ns = int(10 + 30 * (1 - density_ns))
                green_ew = int(10 + 30 * (1 - density_ew))

            # Điều chỉnh theo ba bậc mật độ
            if density_ns > 0.7:
                green_ns = max(green_ns - 5, 5)  # Giảm thời gian đèn xanh
            if density_ew > 0.7:
                green_ew = max(green_ew - 5, 5)  # Giảm thời gian đèn xanh

            red_ns = green_ew + 5
            red_ew = green_ns + 5

        time_ns = max(green_ns, 5)
        time_ew = max(green_ew, 5)

        while time_ns > 0 or time_ew > 0:
            if time_ns == 2 or time_ew == 2:
                payload = {"red": max(red_ns, 5), "green": max(green_ns, 5), "yellow": 5}
                try:
                    async with websockets.connect(WS) as ws:
                        await ws.send(json.dumps(payload))
                    
                    print(Fore.RED + Style.BRIGHT + "📤 Gửi dữ liệu khi đèn sắp đổi:", json.dumps(payload) + Style.RESET_ALL)
                except Exception as e:
                    print("⚠️ WebSocket Error:", e)

            await asyncio.sleep(1)
            if time_ns > 0:
                time_ns -= 1
            if time_ew > 0:
                time_ew -= 1
