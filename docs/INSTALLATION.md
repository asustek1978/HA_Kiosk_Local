# Установка HA Kiosk Local

## Требования

- Android 10+ (API 29+)
- Home Assistant 2026.8+
- планшет и Home Assistant должны иметь сетевой доступ друг к другу

Текущая рабочая связка:

- Android: **v0.3.4.1.2**
- Home Assistant integration: **v0.3.4.1.4**

## Android

После установки HA Kiosk Local:

1. Откройте настройки удержанием **Громкость −**.
2. Укажите URL Home Assistant.
3. Авторизуйтесь в HA внутри WebView.
4. Включите локальный API HA Kiosk Local.
5. Запишите IP, порт и API key.
6. Для настенного режима назначьте HA Kiosk Local приложением Home/Launcher.
7. Разрешите Camera/Microphone, если нужны камера, движение и звук.
8. Для физического выключения экрана разрешите Device Admin.

Рекомендуется закрепить IP планшета в DHCP сервера/роутера.

## Home Assistant через HACS

Добавьте Custom repository:

```text
https://github.com/asustek1978/HA_Kiosk_Local
```

Тип: **Integration**.

Установите HA Kiosk Local, полностью перезапустите Home Assistant и добавьте интеграцию через **Настройки → Устройства и службы**.

Введите:

- IP Android-устройства;
- порт (по умолчанию `2323`);
- API key.

## Ручная установка

Скопируйте:

```text
custom_components/ha_kiosk
```

в:

```text
/config/custom_components/ha_kiosk
```

Затем полностью перезапустите Home Assistant.

## Основная камера

В integration v0.3.4.1.4 основная `Камера планшета` работает через Home Assistant proxy:

```text
Tablet /api/camera/mjpeg (LAN only)
        ↓
Home Assistant
        ↓
/api/camera_proxy_stream
        ↓
local / remote client
```

Для удалённого просмотра не открывайте порты планшета наружу. Клиент должен иметь доступ только к Home Assistant.

Дополнительные сущности `Камера планшета — RTSP` и `Камера планшета — Direct WebRTC` отключены по умолчанию и не требуются для основной камеры.

## Проверка API с Windows

```powershell
Invoke-RestMethod `
  -Uri "http://192.168.1.118:2323/api/status" `
  -Headers @{"X-HA-Kiosk-Key"="ВАШ_API_KEY"}
```

При рабочем соединении ответ содержит `ok = true` и состояние устройства.

## Обновление APK

Для обновления поверх существующей установки Android package не меняется: `com.hakiosk.app`.

Через ADB:

```cmd
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" install -r "HA_Kiosk_Local.apk"
```

APK должен быть подписан тем же ключом, что и уже установленная версия. Также APK можно выбрать через сервисное меню HA Kiosk Local, если приложению разрешена установка из этого источника.
