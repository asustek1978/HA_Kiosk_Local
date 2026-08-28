# HA Kiosk

**HA Kiosk** — Android kiosk-приложение и локальная интеграция для Home Assistant. Приложение открывает Lovelace в полноэкранном WebView, умеет работать как домашний экран Android, передаёт телеметрию планшета в Home Assistant и принимает команды управления по локальной сети.

Текущая связка:

- Android-приложение: **v0.3.1.4**
- Home Assistant integration: **v0.3.1.3**
- Android: **10+ (API 29+)**
- target / compile SDK: **34 (Android 14)**
- Home Assistant: **2026.8+**
- API: локальный HTTP, порт по умолчанию **2323**, авторизация API-ключом

> [!IMPORTANT]
> HA Kiosk не требует облака и MQTT. Home Assistant должен иметь сетевой доступ к планшету. Не пробрасывайте порт API HA Kiosk в Интернет.

## Возможности

### Kiosk / WebView

- полноэкранный Home Assistant;
- сохранение авторизации WebView;
- отсутствие перезагрузки Lovelace при повороте экрана;
- автозапуск и режим Home / Launcher;
- PIN-защищённые настройки, открытие удержанием **Громкость −**;
- keep-screen-on, яркость **0–100%**;
- watchdog WebView, Reload, Home, Restart app;
- установка обновления APK из сервисного меню;
- edge-swipe Reload: слева направо, справа налево или оба направления.

### Камера и присутствие

- нативная WebRTC-камера планшета в Home Assistant;
- видео + микрофон;
- передняя/задняя камера, 480p/720p/1080p, 15/20/24/30 FPS;
- детектор движения;
- детектор уровня звука;
- пробуждение экрана по движению и/или звуку;
- выключение экрана после заданного времени без активности;
- WebRTC временно освобождает монитор движения/света, чтобы не было постоянного конфликта `CAMERA_IN_USE`.

### Освещённость

Три режима источника света:

- **Авто: lux → камера** — настоящий датчик освещённости, а при его отсутствии камера;
- **Только датчик lux**;
- **Только камера** — относительная яркость кадра 0–100%.

Если экран был выключен логикой «темно», он может автоматически проснуться после устойчивого увеличения освещённости. Проценты камеры **не являются lux**.

### Телеметрия Home Assistant

- батарея, зарядка, напряжение, ток, средний ток, мощность и нагрузка;
- температура и состояние аккумулятора, счётчики заряда/энергии при поддержке железом;
- скорость заряда/разряда и оценка времени;
- Wi-Fi RSSI, IP, Android version, версия HA Kiosk, uptime;
- CPU load / температура CPU (если доступна);
- RAM, память процесса HA Kiosk, swap/zRAM, виртуальная память;
- состояние экрана, камеры, WebRTC, движения, звука и освещённости.

## Установка

### 1. Android-приложение

Если в разделе Releases есть готовый `HA_Kiosk.apk`, его можно установить штатным установщиком Android или через ADB. Если готового APK нет, приложение можно собрать из исходников этого репозитория.

Требования для сборки на Windows:

- JDK 17;
- Android SDK Platform 34;
- доступ в Интернет для первой загрузки Gradle и зависимостей.

```cmd
cd /d D:\HA_Kiosk
.\gradlew.bat clean assembleDebug
```

После успешной сборки в каталоге:

```text
app\build\outputs\apk\debug\
```

будут два одинаковых APK:

```text
app-debug.apk
HA_Kiosk.apk
```

Установка поверх существующей версии:

```cmd
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" install -r "D:\HA_Kiosk\app\build\outputs\apk\debug\HA_Kiosk.apk"
```

> [!NOTE]
> Для обновления поверх установленного приложения APK должен быть подписан тем же сертификатом. Если Android сообщает `INSTALL_FAILED_UPDATE_INCOMPATIBLE`, подпись APK отличается.

После первого запуска:

1. Удерживайте **Громкость −**, чтобы открыть настройки.
2. Укажите URL Home Assistant.
3. Включите локальный API.
4. Запишите IP планшета, порт (обычно `2323`) и API key.
5. При необходимости выберите **HA Kiosk** как приложение «Главный экран / Home».
6. Выдайте разрешения камеры и микрофона, если используются WebRTC/движение/звук.

Подробнее: [docs/INSTALLATION.md](docs/INSTALLATION.md)

### 2. Интеграция Home Assistant через HACS

В HACS:

1. Откройте **HACS → ⋮ → Custom repositories**.
2. Добавьте:

```text
https://github.com/asustek1978/HA_Kiosk
```

3. Тип: **Integration**.
4. Установите **HA Kiosk**.
5. Полностью перезапустите Home Assistant.
6. Откройте **Настройки → Устройства и службы → Добавить интеграцию → HA Kiosk**.
7. Введите IP планшета, порт и API key из настроек приложения.

### Ручная установка интеграции

Скопируйте:

```text
custom_components/ha_kiosk
```

в:

```text
/config/custom_components/ha_kiosk
```

и полностью перезапустите Home Assistant.

Иконка/логотип интеграции находятся в `custom_components/ha_kiosk/brand/`. Home Assistant 2026.3+ умеет использовать локальные brand images custom integrations.

## Device Admin и Device Owner

Это **разные** уровни прав:

- **Device Admin** нужен HA Kiosk для полноценного выключения/блокировки экрана;
- **Device Owner** нужен для системной кнопки **«Перезагрузить планшет / телефон»** и расширенного kiosk-управления.

Для Device Owner используется:

```cmd
adb shell dpm set-device-owner com.hakiosk.app/.KioskDeviceAdminReceiver
```

Android может отказать, если на устройстве есть аккаунты:

```text
Not allowed to set the device owner because there are already some accounts on the device
```

Перед provisioning Device Owner Android требует отсутствие аккаунтов. На части устройств также требуется ещё не завершённое первоначальное provisioning; в таком случае может понадобиться заводской сброс. **Не сбрасывайте рабочий планшет, пока не готовы заново его настроить.**

Полная инструкция и типовые ошибки: [docs/DEVICE_OWNER.md](docs/DEVICE_OWNER.md)

## Частые проблемы

| Симптом | Что проверить |
|---|---|
| `device unauthorized` | Разблокировать планшет и подтвердить RSA-разрешение USB debugging |
| `adb server is out of date` | Использовать `adb.exe` из актуального Android SDK `platform-tools` |
| `unknown command` в Home Assistant | Android-приложение и интеграция HA разных поколений API; обновить обе части |
| `CAMERA_IN_USE (4)` | Другая программа/старый монитор держит камеру; v0.3.1.2+ умеет временно освобождать камеру для WebRTC |
| Нет lux | На планшете может не быть физического light sensor; выбрать `Авто: lux → камера` |
| Кнопка reboot недоступна | HA Kiosk не является Device Owner |
| Интеграция не подключается | Проверить IP, порт 2323, API key, firewall/VLAN и доступ HA → планшет |
| Некоторые батарейные сенсоры `unknown` | Android/контроллер батареи не обязан отдавать CURRENT_NOW, CURRENT_AVERAGE, charge/energy counters |
| После назначения HA Kiosk Home неудобно открыть приложения | Удержать Громкость − → обслуживание планшета → Android settings / сменить Home / установить APK |

Подробно: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Безопасность

API HA Kiosk работает по локальному HTTP и защищён индивидуальным API key. Рекомендуется:

- держать планшет и Home Assistant в доверенной LAN/VLAN;
- не публиковать порт `2323` в Интернет;
- закрепить IP планшета через DHCP reservation;
- не публиковать API key в issue, логах и скриншотах.

Подробнее: [docs/SECURITY.md](docs/SECURITY.md)

## Структура репозитория

```text
HA_Kiosk/
├── app/                         # Android приложение
├── custom_components/
│   └── ha_kiosk/               # Home Assistant integration / HACS
├── docs/
├── gradlew / gradlew.bat
├── hacs.json
└── README.md
```

## Статус проекта

Проект находится в активной разработке. Поведение камеры, батарейных датчиков, thermal zones, Device Owner и фоновых сервисов может различаться между производителями Android-устройств.
