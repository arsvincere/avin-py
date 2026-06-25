# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from abc import ABC, abstractmethod

from avin.core.category import Category
from avin.core.exchange import Exchange
from avin.core.iid import Iid


class Asset(ABC):
    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def __hash__(self) -> int: ...

    @abstractmethod
    def __eq__(self, other: object) -> bool: ...

    @abstractmethod
    def iid(self) -> Iid: ...

    @abstractmethod
    def exchange(self) -> Exchange: ...

    @abstractmethod
    def category(self) -> Category: ...

    @abstractmethod
    def ticker(self) -> str: ...

    @abstractmethod
    def figi(self) -> str: ...

    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def lot(self) -> int: ...

    @abstractmethod
    def step(self) -> float: ...
