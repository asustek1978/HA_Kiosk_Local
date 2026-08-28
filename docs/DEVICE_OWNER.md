# Device Owner / Device Admin

## Чем отличаются

**Device Admin** — старый Android admin API. HA Kiosk использует его для полноценного выключения/блокировки экрана.

**Device Owner** — режим владельца управляемого устройства. Он нужен HA Kiosk для системной перезагрузки Android и является правильной основой для dedicated/kiosk device.

## Перед началом

Device Owner provisioning имеет ограничения Android. На тестовом Android 10 успешно потребовалось удалить все Android accounts перед выполнением команды.

Официальная Android Enterprise документация для fully managed device также требует проверить, что на устройстве нет других пользователей/work profile и **нет аккаунтов** перед `dpm set-device-owner`.

## ADB авторизация

Используйте актуальный ADB из Android SDK:

```cmd
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" kill-server
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" start-server
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" devices
```

На планшете подтвердите диалог **«Разрешить отладку по USB»** и при желании поставьте «Всегда разрешать с этого компьютера».

Если `devices` показывает:

```text
unauthorized
```

отзовите USB debugging authorizations в Developer options, переподключите кабель и подтвердите RSA-ключ снова.

## Ошибка с аккаунтами

Если команда:

```cmd
adb shell dpm set-device-owner com.hakiosk.app/.KioskDeviceAdminReceiver
```

возвращает:

```text
Not allowed to set the device owner because there are already some accounts on the device
```

удалите системные аккаунты в Android:

- Google;
- аккаунт производителя;
- Exchange и другие аккаунты, зарегистрированные через Android AccountManager.

Затем повторите команду.

Проверить наличие аккаунтов можно:

```cmd
adb shell dumpsys account
```

После успешного Device Owner provisioning аккаунты можно попробовать добавить обратно. Возможность и ограничения зависят от прошивки и применённых политик.

## Команда Device Owner

```cmd
adb shell dpm set-device-owner com.hakiosk.app/.KioskDeviceAdminReceiver
```

Успешный результат выглядит примерно так:

```text
Success: Device owner set to package
ComponentInfo{com.hakiosk.app/com.hakiosk.app.KioskDeviceAdminReceiver}
```

После этого в HA Kiosk / Home Assistant должен появиться `Device Owner = on`, а кнопка **«Перезагрузить планшет / телефон»** станет доступна.

## Если Android сообщает, что устройство уже provisioned

Некоторые прошивки разрешают назначение владельца только в процессе первоначальной настройки устройства. В этом случае может потребоваться factory reset и provisioning до добавления аккаунтов.

> Не выполняйте factory reset только ради reboot-кнопки, если планшет уже настроен и вы не готовы восстановить его конфигурацию.

## Полезные официальные материалы

- Android Debug Bridge / `dpm set-device-owner`: https://developer.android.com/tools/adb
- Android Enterprise — fully managed device: https://developer.android.com/work/guide
- Dedicated devices cookbook: https://developer.android.com/work/dpc/dedicated-devices/cookbook
