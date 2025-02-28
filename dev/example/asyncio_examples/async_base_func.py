#!/usr/bin/env  python3
# FILE:         tmp.py
# CREATED:      2023.09.24
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

import logging

logger = logging.getLogger("LOGGER")
console_log = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
)
console_log.setFormatter(formatter)
console_log.setLevel(logging.INFO)
logger.addHandler(console_log)
logger.setLevel(logging.INFO)

import sys

sys.path.append("/home/alex/AVIN/")
sys.path.append("/usr/lib/python3.11/site-packages")
sys.path.append("/home/alex/.local/lib/python3.11/site-packages/tinkoff")
sys.path.append("/home/alex/.local/lib/python3.11/site-packages/tinkoff/invest")
import bisect
import collections
import dataclasses
import importlib
import json
import random
import time as timer
import typing
import uuid
from datetime import date, datetime, time, timedelta

import numpy as np
import pandas as pd
from tinkoff.invest import (
    CandleInstrument,
    Client,
    InfoInstrument,
    SubscriptionInterval,
)

from avin.company import *
from avin.const import *
from avin.core import *
from avin.gui import *
from avin.utils import *

TOKEN = (
    "t.ft4wS11u1nCcPALQeW59yJxH3cwXqVBy0DEdwoGE00kPlF5U-7ZX0p_"
    "E2uGuFELbvya9r8vTGKDi22svrIKDcw"
)
# ----------------------------------------------------------------------------


# SuperFastPython.com
# пример, где запускают множество задач, а после этого получают к ним доступ
import asyncio


# корутина для задач
async def task_coroutine(value):
    # вывод сообщения
    print(f"task {value} is running")
    # краткая блокировка
    r = random.random()
    await asyncio.sleep(r)
    print(f"task {value} after sleep {r}")


# определение главной корутины
async def main():
    # вывод сообщения
    print("main coroutine started")
    # запуск нескольких задач
    started_tasks = [asyncio.create_task(task_coroutine(i)) for i in range(10)]
    # выделение времени, необходимого на то, чтобы некоторые из задач запустились
    await asyncio.sleep(0.5)
    # получение всех задач
    tasks = asyncio.all_tasks()
    # вывод сведений обо всех задачах
    for task in tasks:
        print(f"> {task.get_name()}, {task.get_coro()}")
    # ждём завершения всех задач
    for task in started_tasks:
        await task


# запуск asyncio-программы
asyncio.run(main())
exit(1)


# --------------------------- другие примеры работы с asyncio
# определение корутины
async def data_stream():
    # ожидание другой корутины
    print(1)
    await asyncio.sleep(1)
    print(11)


async def main():
    # создание корутины
    # stream = data_stream()
    # проверка типа корутины
    # print(type(stream))
    await data_stream()
    print(2)

    # создаём новый цикл событий asyncio и обеспечиваем доступ к нему
    loop = asyncio.new_event_loop()
    # сообщаем стандартные сведения о цикле
    print(loop)

    stream = data_stream()
    # создание задачи из корутины
    task = asyncio.create_task(stream)
    # создание задачи из корутины в одну строку
    # task = asyncio.create_task(task_coroutine())
    print(task)
    await task

    # проверка на завершение выполнения задачи
    if task.done():
        ...

    # проверка на отмену выполнения задачи
    # task.cancel() - для отмены
    if task.cancelled():
        ...

    # получение возвращённого значения из обёрнутой корутины
    value = task.result()

    try:
        # получение возвращённого значения из обёрнутой корутины
        value = task.result()
    except Exception:
        # задача завершилась неудачно, результата нет
        ...

    # если задача была отменена при вызове result, будет исключение
    # CancelledError
    try:
        # получение возвращённого значения из обёрнутой корутины
        value = task.result()
    except asyncio.CancelledError:
        # задача была отменена
        ...

    # ...
    # проверка того, не была ли отменена задача
    if not task.cancelled():
        # получение возвращённого значения из обёрнутой корутины
        value = task.result()
    else:
        # задача была отменена
        ...

    # если задача не была завершена result вызовет исключение InvalidStateError
    try:
        # получение возвращённого значения из обёрнутой корутины
        value = task.result()
    except asyncio.InvalidStateError:
        # выполнение задачи ещё не завершено
        ...

    # правильно сделать так
    # проверка того, завершено ли выполнение задачи
    if not task.done():
        await task
    # получение возвращённого значения из обёрнутой корутины
    value = task.result()

    # проверка того, не была ли отменена задача
    if not task.cancelled():
        # получение исключения, вызванного задачей
        exception = task.exception()
    else:
        # задача была отменена
        ...

    # проверка того, не было ли завершено выполнение задачи
    if not task.done():
        await task
    # получение исключения, выданного задачей
    exception = task.exception()

    # отмена задачи
    was_cancelled = task.cancel()  # bool

    # функция-коллбэк, вызываемая после завершения работы задачи
    def handle(task):
        print(task)

    ...
    # регистрация коллбэка
    task.add_done_callback(handle)

    # удаление коллбэка, вызываемого при завершении задачи
    task.remove_done_callback(handle)

    # Имя можно задать при создании задачи из корутины
    task = asyncio.create_task(task_coroutine(), name="MyTask")
    # Имя задаче можно назначить и с помощью метода set_name():
    task.set_name("MyTask")
    # Узнать имя задачи можно, воспользовавшись методом get_name():
    name = task.get_name()

    # получение текущей задачи
    task = asyncio.current_task()
    # пример получения текущей задачи из главной корутины
    import asyncio

    # определение главной корутины
    async def main():
        # вывод сообщения
        print("main coroutine started")
        # получение текущей задачи
        task = asyncio.current_task()
        # вывод сведений о ней
        print(task)

    # запуск asyncio-программы
    asyncio.run(main())
    asyncio.transports

    # получение всех задач
    tasks = asyncio.all_tasks()


if __name__ == "__main__":
    asyncio.run(main())
