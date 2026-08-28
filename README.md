# HA Kiosk Local

**HA Kiosk Local** — локальное Android kiosk-приложение и интеграция для Home Assistant. Оно открывает Home Assistant в полноэкранном WebView, превращает планшет/телефон в настенную HA-панель, передаёт телеметрию устройства и принимает локальные команды управления.

> Проект работает локально: без облака и без MQTT. Home Assistant подключается к API планшета напрямую по локальной сети.

## Текущая версия

- Android-приложение: **v0.3.2**
- Home Assistant integration: **v0.3.2**
- Android: **10+ (API 29+)**
- target / compile SDK: **34 (Android 14)**
- Home Assistant: **2026.8+**
- API: локальный HTTP, порт по умолчанию **2323**, доступ по API key

## Возможности

### Kiosk / Home Assistant

- полноэкранный Home Assistant WebView;
- сохранение авторизации;
- без перезагрузки Lovelace при повороте экрана;
- Home / Launcher режим и автозапуск после загрузки;
- настройки по удержанию **Громкость −**;
- PIN-защита настроек;
- яркость **0–100%**;
- Reload, Home, restart приложения, watchdog WebView;
- установка APK из сервисного меню;
- Reload свайпом от левого/правого края.

### Камера, движение, звук

- WebRTC-камера планшета в Home Assistant;
- видео + звук с микрофона;
- передняя/задняя камера;
- 480p / 720p / 1080p;
- 15 / 20 / 24 / 30 FPS;
- детектор движения;
- детектор уровня звука;
- включение экрана по движению и/или звуку;
- выключение экрана после настраиваемого времени без активности;
- защита от конфликта `CAMERA_IN_USE` между монитором движения и WebRTC.

### Освещённость

Поддерживаются два источника и автоматический выбор:

1. **Аппаратный датчик света** — реальные lux, если датчик есть в устройстве.
2. **Камера** — относительный уровень света 0–100%, если датчика lux нет.
3. **Авто: lux → камера** — рекомендуемый режим.

Экран может выключаться после заданного времени в темноте и включаться при устойчивом увеличении освещённости. Значение камеры в процентах не является измерением lux.

### Телеметрия

В Home Assistant могут отображаться:

- уровень батареи и состояние зарядки;
- ток, средний ток, напряжение, мощность и нагрузка аккумулятора;
- температура аккумулятора;
- скорость зарядки/разрядки и оценка оставшегося времени;
- Wi-Fi RSSI и IP;
- Android version и версия HA Kiosk Local;
- uptime;
- CPU load и температура CPU, если доступна;
- RAM, память процесса, swap/zRAM, виртуальная память;
- состояние экрана, WebRTC, камеры, движения, звука и освещённости.

Некоторые батарейные/thermal значения зависят от железа и прошивки Android и могут быть недоступны.

## Установка Home Assistant integration через HACS

1. Откройте **HACS → ⋮ → Custom repositories**.
2. Добавьте репозиторий:

```text
https://github.com/asustek1978/HA_Kiosk_Local
```

3. Тип: **Integration**.
4. Установите **HA Kiosk Local**.
5. Полностью перезапустите Home Assistant.
6. Откройте **Настройки → Устройства и службы → Добавить интеграцию → HA Kiosk Local**.
7. Введите IP планшета, порт (по умолчанию `2323`) и API key из настроек Android-приложения.

### Ручная установка интеграции

Скопируйте каталог:

```text
custom_components/ha_kiosk
```

в:

```text
/config/custom_components/ha_kiosk
```

и полностью перезапустите Home Assistant.

> Внутренний domain остаётся `ha_kiosk`. Это сделано специально, чтобы обновление с ранних версий не создавало вторую интеграцию и новые entity_id.

## Android-приложение

После установки/обновления откройте настройки удержанием **Громкость −**:

1. задайте URL Home Assistant;
2. включите локальный API;
3. запишите IP, порт и API key;
4. при необходимости сделайте **HA Kiosk Local** приложением Home/Launcher;
5. выдайте разрешения Camera/Microphone для WebRTC, движения и звука;
6. для настоящего выключения экрана разрешите Device Admin.

Внутренний Android package остаётся:

```text
com.hakiosk.app
```

Это позволяет устанавливать новые версии поверх уже настроенного HA Kiosk и сохраняет Device Owner.

## Device Owner и удалённая перезагрузка Android

Для системной команды **«Перезагрузить планшет / телефон»** одного Device Admin недостаточно. HA Kiosk Local должен быть **Device Owner**.

После включения USB debugging и авторизации ADB:

```cmd
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" devices
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" shell dpm set-device-owner com.hakiosk.app/.KioskDeviceAdminReceiver
```

### Ошибка: на устройстве есть аккаунты

Android может ответить:

```text
Not allowed to set the device owner because there are already some accounts on the device
```

На Android 10 в нашем тестировании помогло **временно удалить системные аккаунты** (Google и другие) из Android, затем повторить `set-device-owner`. После успешного назначения Device Owner аккаунты можно попробовать добавить обратно.

На некоторых прошивках Android может дополнительно требовать заводской сброс / первоначальное provisioning. Не сбрасывайте рабочее устройство, пока не готовы настроить его заново.

Подробнее: [docs/DEVICE_OWNER.md](docs/DEVICE_OWNER.md)

## Частые проблемы

| Ошибка / симптом | Решение |
|---|---|
| `device unauthorized` | Разблокировать Android и подтвердить RSA-ключ USB debugging |
| `adb server is out of date` | Использовать `adb.exe` из актуального Android SDK `platform-tools` |
| `unknown command` | Android-приложение и HA integration разных версий API — обновить обе части |
| `CAMERA_IN_USE (4)` | Камеру держит другой клиент; актуальная версия освобождает monitor перед WebRTC и повторяет подключение |
| Датчик света отсутствует | Выбрать `Авто: lux → камера`; будет использоваться относительная яркость камеры |
| В темноте экран гаснет, но не просыпается | Проверить актуальную версию, foreground monitor и порог пробуждения/гистерезис |
| Reboot не работает | Проверить, что HA Kiosk Local является Device Owner |
| HA не подключается к планшету | Проверить IP, порт `2323`, API key, VLAN/firewall и маршрут HA → Android |
| Батарейный ток/средний ток `unknown` | Контроллер батареи/прошивка Android может не отдавать эти свойства |
| После выбора HA Kiosk Local как Home нет доступа к приложениям | Удержать Громкость − → обслуживание → Android settings / сменить Home / установить APK |

Подробнее: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Безопасность

API работает по локальному HTTP и защищён индивидуальным API key.

Рекомендуется:

- не пробрасывать порт `2323` в Интернет;
- использовать доверенную LAN/VLAN;
- закрепить IP планшета через DHCP reservation;
- не публиковать API key в issue, скриншотах и логах.

Подробнее: [docs/SECURITY.md](docs/SECURITY.md)

## Структура HACS integration

```text
custom_components/
└── ha_kiosk/
    ├── __init__.py
    ├── api.py
    ├── binary_sensor.py
    ├── button.py
    ├── camera.py
    ├── config_flow.py
    ├── const.py
    ├── coordinator.py
    ├── entity.py
    ├── manifest.json
    ├── number.py
    ├── select.py
    ├── sensor.py
    ├── switch.py
    ├── text.py
    ├── translations/
    └── brand/
```

Иконка интеграции совпадает с иконкой Android-приложения.

## Обновление с HA Kiosk

Переименование в **HA Kiosk Local** не меняет технические идентификаторы:

- Android package: `com.hakiosk.app`
- Home Assistant domain: `ha_kiosk`

Поэтому существующее приложение обновляется поверх старого, а существующая config entry Home Assistant продолжает использоваться.

## Документация

- [Установка](docs/INSTALLATION.md)
- [Device Owner](docs/DEVICE_OWNER.md)
- [Решение проблем](docs/TROUBLESHOOTING.md)
- [Безопасность](docs/SECURITY.md)

## Статус

Проект находится в активной разработке. Android-прошивки производителей заметно отличаются, особенно в работе камеры, фоновых сервисов, Device Owner, батарейной телеметрии и thermal sensors.
