# Troubleshooting

## `adb server is out of date`

Обычно в PATH лежит старый `adb.exe`. Используйте версию из актуального Android SDK:

```cmd
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" devices
```

## `device unauthorized`

Разблокируйте планшет и подтвердите RSA-диалог USB debugging. Если диалог не появляется:

1. Developer options → Revoke USB debugging authorizations.
2. Выключить/включить USB debugging.
3. Переподключить USB.
4. Снова выполнить `adb devices`.

## `Not allowed to set the device owner because there are already some accounts on the device`

Перед `set-device-owner` удалите Android accounts. См. [DEVICE_OWNER.md](DEVICE_OWNER.md).

## `Not allowed to set the device owner because the device is already provisioned`

Ограничение конкретной прошивки/версии Android. Может потребоваться factory reset и provisioning Device Owner до обычной первичной настройки.

## Home Assistant: `unknown command`

Это почти всегда несовместимые поколения Android API и Home Assistant integration. Обновите **обе** части проекта. Для новых optional controls интеграция также проверяет `api_capabilities` устройства.

## `CAMERA_IN_USE (4)` / `MAX_CAMERAS_IN_USE (5)`

Android сообщает, что камеру уже использует другой клиент.

В HA Kiosk v0.3.1.2+:

- монитор движения/света не должен держать камеру одновременно с WebRTC;
- перед WebRTC выполняется освобождение Camera2;
- временная занятость камеры повторяется без постоянной ошибки;
- после закрытия WebRTC монитор автоматически восстанавливается.

Если ошибка остаётся, закройте другие приложения, использующие камеру, и проверьте, не осталась ли старая версия HA Kiosk.

## Видео есть, звука нет

- Проверьте Android microphone permission.
- В HA Kiosk включите «Микрофон камеры».
- Браузер Home Assistant может начать WebRTC muted до пользовательского действия — включите звук в плеере.

## Нет аппаратного датчика освещённости

Это нормально для части планшетов. В HA Kiosk выберите:

```text
Авто: lux → камера
```

Тогда при отсутствии Android `TYPE_LIGHT` используется относительная яркость кадра 0–100%.

Проценты камеры — **не настоящие lux**. Для них используется отдельный порог.

## Экран выключился в темноте и не просыпается

В актуальных версиях монитор использует partial wake lock и умеет пробуждать экран после перехода выше порога + гистерезиса. Проверьте:

- выбран ли рабочий источник света;
- не стоит ли слишком высокий порог пробуждения;
- запущен ли монитор присутствия;
- разрешены ли camera/microphone permissions, если источник/детекторы используют камеру/звук.

## Reboot-кнопка в Home Assistant недоступна

Нужен именно **Device Owner**, не только Device Admin.

## Некоторые сенсоры батареи `unknown`

Android BatteryManager properties зависят от контроллера батареи и прошивки. Устройство может не отдавать:

- current now;
- current average;
- charge counter;
- energy counter.

Это не обязательно ошибка HA Kiosk.

## Интеграция не находится после ручного копирования

Проверьте структуру:

```text
/config/custom_components/ha_kiosk/manifest.json
/config/custom_components/ha_kiosk/__init__.py
...
```

После копирования выполните полный restart Home Assistant. При необходимости обновите frontend с очисткой кэша.

## Интеграция `cannot_connect`

Проверьте:

- IP устройства;
- локальный API включён;
- порт совпадает (default 2323);
- HA имеет маршрут до планшета;
- firewall/VLAN не блокирует TCP;
- приложение не было выгружено прошивкой Android.

Проверка API:

```powershell
Invoke-RestMethod `
  -Uri "http://IP:2323/api/status" `
  -Headers @{"X-HA-Kiosk-Key"="KEY"}
```

## `invalid_auth`

API key в Home Assistant не совпадает с ключом в приложении. Скопируйте его заново без пробелов.

## После назначения HA Kiosk главным экраном невозможно попасть в приложения

Удерживайте **Громкость −** → обслуживание планшета. Там доступны:

- Android settings;
- смена Home/Launcher;
- разрешение установки APK;
- установка обновления HA Kiosk.

В аварийном случае можно обновить приложение через `adb install -r`.
