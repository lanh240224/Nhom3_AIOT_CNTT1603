#include "esp_camera.h"
#include <WiFi.h>

#define CAMERA_MODEL_AI_THINKER  // Định nghĩa mô hình camera
#include "camera_pins.h"

// ===========================
// Thông tin WiFi
// ===========================
const char *ssid = "Nha Tro Anh Cuong";
const char *password = "88888888";

// ===========================
// Khai báo cấu hình mạng tĩnh
// ===========================
IPAddress local_IP(192, 168, 100, 154);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress primaryDNS(8, 8, 8, 8);
IPAddress secondaryDNS(8, 8, 4, 4);

// ===========================
// Cấu hình LED flash
// ===========================
#define FLASH_LED_PIN 4

void setupLedFlash() {
  pinMode(FLASH_LED_PIN, OUTPUT);
  digitalWrite(FLASH_LED_PIN, LOW);
}

void turnOnFlash() {
  digitalWrite(FLASH_LED_PIN, HIGH);
}

void turnOffFlash() {
  digitalWrite(FLASH_LED_PIN, LOW);
}

// ===========================
// Khai báo Server Camera
// ===========================
void startCameraServer();

void setup() {
  Serial.begin(115200);
  Serial.println();

  setupLedFlash();  // Cấu hình đèn flash

  // ===========================
  // Cấu hình Camera
  // ===========================
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  if (psramFound()) {
    config.jpeg_quality = 10;
    config.fb_count = 2;
    config.grab_mode = CAMERA_GRAB_LATEST;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.fb_location = CAMERA_FB_IN_DRAM;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);
    s->set_brightness(s, 1);
    s->set_saturation(s, -2);
  }

  // ===========================
  // Kết nối WiFi
  // ===========================
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("⚠️ Không thể đặt IP tĩnh, sử dụng DHCP...");
  }

  Serial.print("🔗 Đang kết nối WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ Đã kết nối WiFi!");

  // 🔦 Bật đèn flash khi kết nối WiFi thành công
  turnOnFlash();
  delay(2000);  // Giữ đèn sáng 2 giây
  turnOffFlash();

  startCameraServer();

  Serial.print("🌐 Camera Ready! Truy cập: http://");
  Serial.println(WiFi.localIP());
}

void loop() {
  // turnOnFlash();
}
