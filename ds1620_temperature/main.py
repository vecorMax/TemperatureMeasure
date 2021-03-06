# -*- coding: utf-8 -*-
# *******************************************************************************************************
# Селетков И.П. 2018 1125.                                                                              *
# Программа для тестирования обмена сообщениями через сервер NATS.                                      *
# *******************************************************************************************************
import traceback
import sys
import datetime
import asyncio
import json
import uuid
import configparser
# Импортируем библиотеку по работе с GPIO
import RPi.GPIO as GPIO
# Подключаем библиотечный файл для отправки сообщений.
from smt.rpi.nats.messaging.CServiceMessaging import CServiceMessaging
# Импортируем класс для работы с датчиком ds1620
from drivers.ds1620driver import DS1620
# Подключаем конфигурационны файл
from configManager.CConfigManager import CConfigManager


async def cycle():
    global delay
    global t_sensor
    print("Начало работы программы.")
    messaging = CServiceMessaging()

    # === Инициализация пинов для светодиода ===
    GPIO.setmode(GPIO.BCM)
    pin_led = 5
    pin_switch = 4
    GPIO.setup(pin_led, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(pin_switch, GPIO.OUT, initial=GPIO.HIGH)

    # Обновление параметров программы (частота опроса датчика)
    # из конфигурационного файла
    delay = CConfigManager.get_setting(path, 'Settings', 'timedelay')

    # Инициализация old_temperature по умолчанию
    old_temperature = 0.0

    mode = 1
    while 1:
        if mode == 1:
            GPIO.output(pin_led, GPIO.HIGH)
        else:
            GPIO.output(pin_led, GPIO.LOW)

        # Считываем температуру
        temperature = t_sensor.get_temperature()

        # Обновляем частоту опроса датчика, если пришло на сервер пришло соответствующее уведомление
        delay = CServiceMessaging.change_delay(delay, 1)

        # Отправляем сообщение о текущем режиме на сервер.
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        if temperature is not None:
            s_temperature = "{:3.0f}".format(temperature)
            message = f'|{current_time} | {mode} | {s_temperature}°C |'
        else:
            message = f'{current_time} Не удалось прочитать значение с датчика'
        print(message)

        # Создаем объект JSON, для передачи UUID платы,
        # объекта измерения, время измерения, mode, частота измерения и данные измерения
        output = json.dumps(
            {"UUID": str(uuid.uuid1()),
             "ObjectMeasure": "Temperature",
             "CurrentTime": current_time,
             "Mode": mode,
             "Delay": delay,
             "Data": temperature
             }
        )

        # Отправка данных на сервер NATS
        if old_temperature != temperature:
            await asyncio.ensure_future(messaging.send(output))

        # Остановка системы на частоту, заданную пользователем
        delay_int = int(float(delay))
        await asyncio.sleep(delay_int)

        # Переключение модулей
        mode = 1 - mode

        # Запоминаем предыдущее значение температуры
        old_temperature = temperature


async def main():
    try:
        await cycle()
    except KeyboardInterrupt:
        # Выход из программы по нажатию Ctrl+C
        print("Завершение работы Ctrl+C.")
    except Exception as e:
        # Прочие исключения
        print("Ошибка в приложении.")
        # Подробности исключения через traceback
        traceback.print_exc(limit=2, file=sys.stdout)
    finally:
        print("Сброс состояния порта в исходное.")
        # Возвращаем пины в исходное состояние
        GPIO.cleanup()
        # Информируем о завершении работы программы
        print("Программа завершена.")

if __name__ == '__main__':
    # Частота измерения данных с датчика
    delay = 5
    # Название конфигурационного файла
    path = "settings1.ini"
    # Инициализация пинов для датчика температуры: rst, dq, clk
    t_sensor = DS1620(17, 18, 27)
    asyncio.run(main())
