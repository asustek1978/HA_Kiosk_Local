# Changelog

## Home Assistant integration 0.3.4.1.4

- основная `Камера планшета` переведена на HA-proxied MJPEG по модели Fully Kiosk Browser;
- основная камера больше не объявляет `CameraEntityFeature.STREAM`, поэтому frontend использует стандартный `/api/camera_proxy_stream` Home Assistant;
- браузер/телефон подключается только к Home Assistant, прямой внешний доступ к планшету не нужен;
- используется Android endpoint `/api/camera/mjpeg`;
- RTSP/H.264/AAC сохранён как отдельная отключённая по умолчанию сущность `Камера планшета — RTSP`;
- Direct WebRTC сохранён как отдельная отключённая по умолчанию сущность;
- удалённый просмотр основной камеры подтверждён через обычный внешний доступ Home Assistant.

## Home Assistant integration 0.3.4.1.3

- исправлено повторное открытие RTSP-камеры после простоя;
- при новом запросе RTSP выполняется `camera_rtsp_stop` → `camera_rtsp_start` вместо необходимости перезапускать всё приложение;
- глобальные настройки `stream:` Home Assistant не изменяются.

## Android 0.3.4.1.2

- исправлено зеркальное изображение фронтальной камеры в исходящем видеопотоке;
- добавлено самовосстановление RTSP после простоя и неудачных подключений;
- versionCode 19 / versionName 0.3.4.1.2.

## Android / integration 0.3.4.1

- RTSP H.264/AAC server для LAN-only camera path;
- RTSP disconnect grace увеличен до 90 секунд;
- ожидание первого клиента увеличено до 60 секунд;
- H.264 I-frame interval: 1 секунда;
- RTSP cache ограничен 50 кадрами;
- добавлены camera transport / RTSP diagnostics.

## 0.3.2

- проект переименован в **HA Kiosk Local**;
- Android package сохранён как `com.hakiosk.app` для совместимого обновления;
- Home Assistant domain сохранён как `ha_kiosk`;
- унифицированы названия Android и Home Assistant integration;
- обновлены HACS metadata, manifest, translations и документация;
- сохранены WebRTC, motion/sound monitoring, light sensor/camera fallback, Device Owner и system telemetry.

## 0.3.1.x

- расширенная батарейная телеметрия;
- CPU/RAM/swap/zRAM;
- движение и звук;
- auto screen-off при отсутствии;
- light sensor + camera light fallback;
- wake by light;
- исправления `CAMERA_IN_USE`;
- Device Owner reboot;
- brand icon Home Assistant.
