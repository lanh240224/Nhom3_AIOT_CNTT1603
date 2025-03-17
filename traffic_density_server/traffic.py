from camera import get_density_data


def calculate_traffic_lights():
    """Tính toán thời gian đèn dựa trên mật độ xe"""
    density_ns, density_ew = get_density_data()

    green_ns = int(10 + 30 * (1 - density_ns))
    green_ew = int(10 + 30 * (1 - density_ew))

    red_ns = green_ew + 5
    red_ew = green_ns + 5

    return {
        "green_ns": max(green_ns, 5),
        "green_ew": max(green_ew, 5),
        "red_ns": max(red_ns, 5),
        "red_ew": max(red_ew, 5),
        "yellow": 5,
    }
