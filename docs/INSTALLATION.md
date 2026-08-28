# Установка HA Kiosk

## Требования

### Android

- Android 10+ (API 29+)
- Camera/Microphone permissions — только если нужны WebRTC, движение или звук
- Wi-Fi/LAN с доступом к Home Assistant

### Home Assistant

- Home Assistant 2026.8+
- HACS — необязательно, но упрощает установку интеграции

## Установка Android APK

### Через Android

Откройте `HA_Kiosk.apk` и разрешите установку из выбранного источника.

Если HA Kiosk уже назначен Home/Launcher, откройте его настройки удержанием **Громкость −** и используйте раздел обслуживания планшета для установки APK или открытия системных настроек.

### Через ADB

Проверка подключения:

```cmd
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" devices
```

Установка/обновление:

```cmd
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" install -r "HA_Kiosk.apk"
```

Если APK подписан другим ключом, Android не установит его поверх существующей версии. В этом случае сначала разберитесь с подписью — удаление приложения сотрёт его локальные настройки и WebView-сессию.

## Первичная настройка приложения

1. Запустите HA Kiosk.
2. Откройте настройки удержанием **Громкость −**.
3. Укажите URL Home Assistant, например `http://192.168.1.10:8123/dashboard/home`.
4. Включите локальный API HA Kiosk.
5. Оставьте порт `2323` или задайте другой свободный порт.
6. Сохраните API key.
7. Для настоящего kiosk-автозапуска можно назначить HA Kiosk приложением Home.
8. Для полноценного выключения экрана разрешите Device Admin.
9. Для удалённого reboot Android при необходимости настройте Device Owner отдельно.

## Проверка API с Windows

```powershell
Invoke-RestMethod `
  -Uri "http://IP_ПЛАНШЕТА:2323/api/status" `
  -Headers @{"X-HA-Kiosk-Key"="ВАШ_API_KEY"}
```

Ожидается `ok : True` и телеметрия устройства.

## HACS

1. HACS → меню `⋮` → **Custom repositories**.
2. URL: `https://github.com/asustek1978/HA_Kiosk`
3. Category: **Integration**.
4. Установить HA Kiosk.
5. Полностью перезапустить Home Assistant.

Затем:

**Настройки → Устройства и службы → Добавить интеграцию → HA Kiosk**

Введите:

- Host: IP планшета
- Port: обычно `2323`
- API key: из приложения HA Kiosk

## Ручная установка Home Assistant integration

Скопируйте папку:

```text
custom_components/ha_kiosk
```

в:

```text
/config/custom_components/ha_kiosk
```

После копирования требуется полный restart Home Assistant.

## Сетевые рекомендации

- Зарезервируйте IP планшета в DHCP.
- Home Assistant должен напрямую обращаться к `http://IP:2323`.
- Если HA и планшет находятся в разных VLAN, разрешите нужный трафик между ними.
- Не делайте port-forward `2323` на WAN.
