#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

// 🔹 WiFi Credentials
const char *ssid = "Nha Tro Anh Cuong";
const char *password = "88888888";

// 🔹 WebSocket Server
WebSocketsClient webSocket;
const char *websocket_host = "192.168.100.191";  // Đổi thành IP server của bạn
const int websocket_port = 8765;

// 🔹 Chân đèn giao thông
#define RED_NS 15
#define YELLOW_NS 4
#define GREEN_NS 5
#define RED_EW 13
#define YELLOW_EW 12
#define GREEN_EW 27

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("🔄 Đang kết nối WiFi...");
  }
  Serial.println("✅ Kết nối WiFi thành công!");

  // Kết nối WebSocket
  webSocket.begin(websocket_host, websocket_port, "/");
  webSocket.onEvent(webSocketEvent);

  // Cấu hình chân đèn
  pinMode(RED_NS, OUTPUT);
  pinMode(YELLOW_NS, OUTPUT);
  pinMode(GREEN_NS, OUTPUT);
  pinMode(RED_EW, OUTPUT);
  pinMode(YELLOW_EW, OUTPUT);
  pinMode(GREEN_EW, OUTPUT);

  // Tắt tất cả đèn lúc khởi động
  turnOffAllLights();
}

void loop() {
  webSocket.loop();
}

// 🛠 Hàm tắt tất cả đèn
void turnOffAllLights() {
  digitalWrite(RED_NS, LOW);
  digitalWrite(YELLOW_NS, LOW);
  digitalWrite(GREEN_NS, LOW);
  digitalWrite(RED_EW, LOW);
  digitalWrite(YELLOW_EW, LOW);
  digitalWrite(GREEN_EW, LOW);
}

// 🛠 Hàm điều khiển đèn giao thông
void updateTrafficLights(String north_south, String east_west) {
  turnOffAllLights();  // Tắt hết đèn trước khi bật đèn mới

  if (north_south == "red") {
    digitalWrite(RED_NS, HIGH);
    digitalWrite(GREEN_EW, HIGH);
  } else if (north_south == "green") {
    digitalWrite(GREEN_NS, HIGH);
    digitalWrite(RED_EW, HIGH);
  } else if (north_south == "yellow") {
    digitalWrite(YELLOW_NS, HIGH);
    digitalWrite(YELLOW_EW, HIGH);
  }

  Serial.println("✅ Cập nhật đèn giao thông!");
}

// 🛠 Xử lý dữ liệu từ WebSocket
// 🛠 Xử lý dữ liệu từ WebSocket
void webSocketEvent(WStype_t type, uint8_t *payload, size_t length) {
  if (type == WStype_TEXT) {
    Serial.printf("📩 Nhận dữ liệu: %s\n", payload);

    // Phân tích JSON
    DynamicJsonDocument doc(128);
    DeserializationError error = deserializeJson(doc, payload);
    if (error) {
      Serial.println("❌ Lỗi parse JSON!");
      return;
    }

    // Đọc trạng thái đèn từ server (KHÔNG còn "state" bọc ngoài)
    String north_south = doc["north_south"].as<String>();
    String east_west = doc["east_west"].as<String>();

    // Cập nhật đèn giao thông
    updateTrafficLights(north_south, east_west);
  }
}


// #include <WiFi.h>
// #include <WebSocketsClient.h>
// #include <ArduinoJson.h>

// // 🔹 Thông tin WiFi
// const char *ssid = "WIFI GIANG VIEN";  // Đổi thành WiFi của bạn
// const char *password = "dhdn7799";     // Đổi thành mật khẩu của bạn

// // 🔹 WebSocket Server
// WebSocketsClient webSocket;
// const char* websocket_host = "172.16.66.162";  // Đổi thành IP server WebSocket của bạn
// const int websocket_port = 8765;

// // 🔹 Định nghĩa chân đèn giao thông
// #define RED_NS 15
// #define YELLOW_NS 4
// #define GREEN_NS 5
// #define RED_EW 13
// #define YELLOW_EW 12
// #define GREEN_EW 27

// // 🔹 Bật/Tắt IP tĩnh (nếu cần)
// bool useStaticIP = false;
// IPAddress local_IP(192, 168, 1, 150);
// IPAddress gateway(192, 168, 1, 1);
// IPAddress subnet(255, 255, 255, 0);

// void setup() {
//     Serial.begin(115200);
//     Serial.println("\n🚦 Khởi động hệ thống giao thông ESP32...");

//     // In địa chỉ MAC của ESP32
//     Serial.print("🔎 Địa chỉ MAC ESP32: ");
//     Serial.println(WiFi.macAddress());

//     // Kết nối WiFi với debug
//     connectToWiFi();

//     // Kết nối WebSocket
//     webSocket.begin(websocket_host, websocket_port, "/");
//     webSocket.onEvent(webSocketEvent);

//     // Cấu hình chân đèn
//     pinMode(RED_NS, OUTPUT);
//     pinMode(YELLOW_NS, OUTPUT);
//     pinMode(GREEN_NS, OUTPUT);
//     pinMode(RED_EW, OUTPUT);
//     pinMode(YELLOW_EW, OUTPUT);
//     pinMode(GREEN_EW, OUTPUT);

//     // Tắt tất cả đèn lúc khởi động
//     turnOffAllLights();
// }

// void loop() {
//     webSocket.loop();

//     // Nếu bị mất WiFi, thử kết nối lại
//     if (WiFi.status() != WL_CONNECTED) {
//         Serial.println("⚠️ Mất kết nối WiFi! Đang thử kết nối lại...");
//         connectToWiFi();
//     }
// }

// // 🛠 Kết nối WiFi với debug
// void connectToWiFi() {
//     if (useStaticIP) {
//         WiFi.config(local_IP, gateway, subnet);
//         Serial.println("🌐 Đang sử dụng IP tĩnh...");
//     }

//     WiFi.begin(ssid, password);
//     Serial.println("🔄 Đang kết nối WiFi...");

//     int count = 0;
//     while (WiFi.status() != WL_CONNECTED) {
//         delay(1000);
//         Serial.print(".");
//         count++;

//         if (count > 20) {  // Thử tối đa 20 giây
//             Serial.println("\n❌ Không thể kết nối WiFi! Kiểm tra lại SSID và Password.");
//             Serial.print("🔎 Trạng thái WiFi: ");
//             Serial.println(WiFi.status());  // In mã lỗi WiFi
//             return;
//         }
//     }

//     Serial.println("\n✅ Kết nối WiFi thành công!");
//     Serial.print("📡 Địa chỉ IP: ");
//     Serial.println(WiFi.localIP());
// }

// // 🛠 Hàm tắt tất cả đèn
// void turnOffAllLights() {
//     digitalWrite(RED_NS, LOW);
//     digitalWrite(YELLOW_NS, LOW);
//     digitalWrite(GREEN_NS, LOW);
//     digitalWrite(RED_EW, LOW);
//     digitalWrite(YELLOW_EW, LOW);
//     digitalWrite(GREEN_EW, LOW);
// }

// // 🛠 Hàm điều khiển đèn giao thông
// void updateTrafficLights(String north_south, String east_west) {
//     turnOffAllLights();  // Tắt hết đèn trước khi bật đèn mới

//     if (north_south == "red") {
//         digitalWrite(RED_NS, HIGH);
//         digitalWrite(GREEN_EW, HIGH);
//     }
//     else if (north_south == "green") {
//         digitalWrite(GREEN_NS, HIGH);
//         digitalWrite(RED_EW, HIGH);
//     }
//     else if (north_south == "yellow") {
//         digitalWrite(YELLOW_NS, HIGH);
//         digitalWrite(YELLOW_EW, HIGH);
//     }

//     Serial.println("✅ Cập nhật đèn giao thông!");
// }

// // 🛠 Xử lý dữ liệu từ WebSocket
// void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
//     if (type == WStype_TEXT) {
//         Serial.printf("📩 Nhận dữ liệu: %s\n", payload);

//         // Phân tích JSON
//         DynamicJsonDocument doc(256);
//         DeserializationError error = deserializeJson(doc, payload);
//         if (error) {
//             Serial.println("❌ Lỗi parse JSON!");
//             return;
//         }

//         // Đọc trạng thái đèn từ server
//         String north_south = doc["north_south"].as<String>();
//         String east_west = doc["east_west"].as<String>();

//         // Cập nhật đèn giao thông
//         updateTrafficLights(north_south, east_west);
//     }
// }
