# -*- coding: utf-8 -*-
# *******************************************************************************************************
# Класс содержит методы для обмена сообщениями чере сервер NATS.                                        *
# @author Селетков И.П. 2018 1214.                                                                      *
# *******************************************************************************************************
import asyncio
import logging
from nats.aio.client import Client as NATSClientLibrary
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers


class CServiceMessaging:

    # ***************************************************************************************************
    # Конструктор объекта.                                                                              *
    # ***************************************************************************************************
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        self.__nc = NATSClientLibrary()

    # def __enter__(self):
    #     return self
    #
    # def __exit__(self, exc_type, exc_value, traceback):
    #     self.close()

    # ***************************************************************************************************
    # Подключение к серверу NATS.                                                                       *
    # ***************************************************************************************************
    async def __connect(self):
        if not self.__nc.is_connected:
            logging.info("Establishing connection to NATS server.")
            try:
                await self.__nc.connect("192.168.1.103", loop=asyncio.get_running_loop())
                logging.info("Connection to NATS server established.")
            except ErrNoServers as e:
                logging.error("Cannot connect to NATS server.", e)

    # ***************************************************************************************************
    # Отправка сообщения на сервер NATS.                                                                *
    # ***************************************************************************************************
    async def send(self, message):
        await self.__connect()
        if not self.__nc.is_connected:
            return

        await self.__nc.publish("test", message.encode("UTF-8"))

    # ***************************************************************************************************
    # Завершение работы, закрытие соединения с сервером.                                                *
    # ***************************************************************************************************
    async def close(self):
        if not self.__nc.is_connected:
            return
        logging.info("Closing connection to NATS server.")
        await self.__nc.close()
        logging.info("Connection to NATS server closed.")


