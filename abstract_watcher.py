import abc
from typing import Coroutine, Any
import asyncio

"""
Описание задачи:
    Необходимо реализовать планировщик, позволяющий запускать и отслеживать фоновые корутины.
    Планировщик должен обеспечивать:
        - возможность планирования новой задачи
        - отслеживание состояния завершенных задач (сохранение результатов их выполнения)
        - отмену незавершенных задач перед остановкой работы планировщика

    Ниже представлен интерфейс, которому должна соответствовать ваша реализация.
    Обратите внимание, что перед завершением работы планировщика, все запущенные им корутины должны быть
    корректным образом завершены.
    В папке tests вы найдете тесты, с помощью которых мы будем проверять работоспособность вашей реализации
"""


class AbstractRegistrator(abc.ABC):
    """
    Сохраняет результаты работы завершенных задач.
    В тестах мы передадим в ваш Watcher нашу реализацию Registrator и проверим корректность сохранения результатов.
    """

    def __init__(self):
        self.values = []
        self.errors = []

    @abc.abstractmethod
    def register_value(self, value: Any) -> None:
        # Store values returned from done task
        self.values.append(value)

    @abc.abstractmethod
    def register_error(self, error: BaseException) -> None:
        # Store exceptions returned from done task
        self.errors.append(error)


class AbstractWatcher(abc.ABC):
    """
    Абстрактный интерфейс, которому должна соответсвовать ваша реализация Watcher.
    При тестировании мы расчитываем на то, что этот интерфейс будет соблюден.
    """

    def __init__(self, registrator: AbstractRegistrator):
        self.registrator = registrator  # we expect to find registrator here
        self.tasks = set()

    @abc.abstractmethod
    async def start(self) -> None:
        # Good idea is to implement here all necessary for start watcher :)
        ...

    @abc.abstractmethod
    async def stop(self) -> None:
        # Method will be called on the end of the Watcher's work
        ...

    @abc.abstractmethod
    def start_and_watch(self, coro: Coroutine) -> None:
        # Start new task and put to watching
        ...


class StudentWatcher(AbstractWatcher):
    def register_errors_and_values(self):
        for task in self.tasks:
            try:
                self.registrator.register_value(task.result())
            except BaseException as e:
                self.registrator.register_error(e)

    async def start(self) -> None:
        if self.tasks:
            await asyncio.wait(self.tasks, return_when=asyncio.ALL_COMPLETED)
        self.register_errors_and_values()
        self.tasks.clear()

    async def stop(self) -> None:
        await asyncio.sleep(0.01)
        self.register_errors_and_values()
        map(asyncio.Task.cancel, self.tasks)

    def start_and_watch(self, coro: Coroutine) -> None:
        task = asyncio.create_task(coro)
        self.tasks.add(task)

