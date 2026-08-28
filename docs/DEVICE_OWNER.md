# Device Admin и Device Owner

## Разница

**Device Admin** используется для управления блокировкой/выключением экрана.

**Device Owner** даёт HA Kiosk Local расширенные системные возможности, включая настоящую перезагрузку Android через `DevicePolicyManager.reboot()`.

## Подготовка ADB

Включите Developer options и USB debugging. Используйте актуальный ADB из Android SDK:

```cmd
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" kill-server
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" start-server
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" devices
```

Если устройство отображается как `unauthorized`, разблокируйте планшет и подтвердите RSA-запрос **«Разрешить отладку по USB»**. Желательно поставить галочку **«Всегда разрешать с этого компьютера»**.

## Назначение Device Owner

```cmd
"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" shell dpm set-device-owner com.hakiosk.app/.KioskDeviceAdminReceiver
```

При успехе Android сообщает `Success: Device owner set ...`.

## Ошибка: на устройстве уже есть аккаунты

```text
Not allowed to set the device owner because there are already some accounts on the device
```

Android не разрешает provisioning Device Owner при наличии системных аккаунтов.

На Android 10 рабочий вариант:

1. Открыть Android **Настройки → Аккаунты**.
2. Временно удалить Google и другие зарегистрированные системные аккаунты.
3. Повторить `dpm set-device-owner`.
4. После успешного назначения Device Owner при необходимости попробовать добавить аккаунты обратно.

Удаление аккаунта из Android не равно удалению самой учётной записи Google, но может удалить локально синхронизированные данные этого аккаунта. Убедитесь, что необходимые данные синхронизированы.

## Device already provisioned

Некоторые производители требуют назначать Device Owner только во время первоначальной настройки устройства. В таком случае может потребоваться factory reset.

**Не выполняйте заводской сброс рабочего планшета только ради этой функции, если не готовы настроить устройство заново.**

## Проверка

В HA Kiosk Local должен отображаться статус Device Owner. После обновления Home Assistant кнопка системной перезагрузки становится доступна.
