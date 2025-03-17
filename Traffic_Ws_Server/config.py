# Thời gian mặc định cho đèn giao thông
TIMINGS = {"red": 10, "green": 8, "yellow": 3}

# Trạng thái mặc định của đèn
DEFAULT_TIMINGS = {
    "north_south": "red",
    "east_west": "green",
    "countdown": TIMINGS["red"],
}

# Trạng thái hiện tại của đèn (ban đầu giống mặc định)
traffic_state = DEFAULT_TIMINGS.copy()
