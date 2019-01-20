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
import hashlib
# Импортируем библиотеку по работе с GPIO
import RPi.GPIO as GPIO
# Подключаем библиотечный файл для отправки сообщений.
from smt.rpi.nats.messaging.CServiceMessaging import CServiceMessaging
# Импортируем класс для работы с датчиком ds1620
from drivers.ds1620driver import DS1620


async def cycle():
    print("Начало работы программы.")
    messaging = CServiceMessaging()

    # === Инициализация пинов для светодиода ===
    GPIO.setmode(GPIO.BCM)
    pin_led = 5
    pin_switch = 4
    GPIO.setup(pin_led, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(pin_switch, GPIO.OUT, initial=GPIO.HIGH)

    # Инициализация пинов для датчика температуры: rst, dq, clk
    t_sensor = DS1620(17, 18, 27)

    # Частота измерения данных с датчика
    delay = 5

    mode = 1
    while 1:
        if mode == 1:
            GPIO.output(pin_led, GPIO.HIGH)
        else:
            GPIO.output(pin_led, GPIO.LOW)

        # Считываем температуру
        temperature = t_sensor.get_temperature()

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
             "Object Measure": "Temperature",
             "Current Time": current_time,
             "Mode": mode,
             "Sleep": delay,
             "Data": temperature
             }
        )
        await asyncio.ensure_future(messaging.send(output))

        await asyncio.sleep(delay)
        mode = 1 - mode


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
    asyncio.run(main())
