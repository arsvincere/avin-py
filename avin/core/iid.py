# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from pathlib import Path

from avin.core.category import Category
from avin.core.exchange import Exchange
from avin.core.ticker import Ticker
from avin.utils import Cmd, cfg


class Iid:
    """Instrument id

    # ru
    Идентификатор инструмента, обертка над dict с информацией: тикер,
    имя, биржа, категория, минимальный шаг цены и тп.
    """

    def __init__(self, info: dict):
        assert info["exchange"] is not None
        assert info["category"] is not None
        assert info["ticker"] is not None
        assert info["figi"] is not None
        assert info["name"] is not None
        assert info["lot"] is not None
        assert info["step"] is not None

        self.__info = info

    def __str__(self):
        s = f"{self.exchange().name}_{self.category().name}_{self.ticker()}"
        return s

    @property
    def info(self) -> dict:
        """Return 'dict' with instrument info.

        # ru
        Возвращает 'dict' со всей имеющейся информацией об инструменте.
        """

        return self.__info

    def exchange(self) -> Exchange:
        return Exchange.from_str(self.__info["exchange"])

    def category(self) -> Category:
        return Category.from_str(self.__info["category"])

    def ticker(self) -> Ticker:
        return self.__info["ticker"]

    def figi(self) -> str:
        return self.__info["figi"]

    def name(self) -> str:
        return self.__info["name"]

    def lot(self) -> int:
        return int(self.__info["lot"])

    def step(self) -> float:
        return float(self.__info["step"])

    def path(self) -> Path:
        path = Cmd.path(
            cfg.data,
            self.exchange().name,
            self.category().name,
            self.ticker(),
        )
        return path

    def pretty(self) -> str:
        return Cmd.to_json_str(self.__info, indent=4)

    @classmethod  # from_str
    async def from_str(cls, string: str) -> Iid:
        raise NotImplementedError()

    @classmethod  # from_figi
    async def from_figi(cls, figi: str) -> Iid:
        raise NotImplementedError()


if __name__ == "__main__":
    ...
