import cv2

# Danh sách lưu tọa độ điểm
points = []


# Hàm xử lý sự kiện click chuột
def get_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Khi nhấn chuột trái
        points.append((x, y))
        print(f"Điểm đã chọn: {x}, {y}")

        # Hiển thị điểm trên ảnh
        cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Chọn điểm", img)


# Đọc ảnh từ file
img = cv2.imread("154.jpg")

# Hiển thị ảnh
cv2.imshow("Chọn điểm", img)
cv2.setMouseCallback("Chọn điểm", get_points)

cv2.waitKey(0)
cv2.destroyAllWindows()

# In ra danh sách tọa độ
print("Danh sách tọa độ:", points)
