# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime as DateTime
from pathlib import Path
from typing import Any

import polars as pl

from avin.core.category import Category
from avin.core.chart import Chart
from avin.core.event import BarEvent, TicEvent
from avin.core.exchange import Exchange
from avin.core.footprint import Footprint
from avin.core.iid import Iid
from avin.core.market_data import MarketData
from avin.core.tic import Tic
from avin.core.ticker import Ticker
from avin.core.timeframe import TimeFrame
from avin.manager import Manager
from avin.utils import CFG, ONE_WEEK, Cmd, log, now


class Asset(ABC):
    """Base abstract class for any instruments.

    # ru
    Базовый класс для всех активов.

    Общий интерфейс для конкретных типов активов: акция, фьючерс, облигация,
    индекс и тп. Пока реализована только акция.
    """

    @abstractmethod
    def __init__(self, iid: Iid):
        self.__iid = iid

    def __str__(self):
        return str(self.__iid)

    @classmethod
    @abstractmethod
    def from_str(cls, string: str): ...

    @classmethod
    @abstractmethod
    def from_csv(cls, csv_line: str): ...

    @property
    def iid(self) -> Iid:
        """Return instrument id.

        # ru
        Возвращает ссылку на идентификатор инструмента.
        """
        return self.__iid

    def exchange(self) -> Exchange:
        """Return exchange.

        # ru
        Возвращает биржу на которой торгуется инструмент.
        """
        return self.__iid.exchange()

    def category(self) -> Category:
        """Return category.

        # ru
        Возвращает категорию инструмента.
        """

        return self.__iid.category()

    def ticker(self) -> Ticker:
        """Return ticker.

        # ru
        Возвращает тикер инструмента.
        """

        return self.__iid.ticker()

    def figi(self) -> str:
        """Return FIGI - Financial Instrument Global Identifier.

        # ru
        Возвращает FIGI - глобальный финансовый идентификатор
        инструмента. Используется брокером при выставлении ордера,
        так как тикер не является уникальным идентификатором, однозначно
        определяющим актив.
        """

        return self.__iid.figi()

    def name(self) -> str:
        """Return instrument name.

        # ru
        Возвращает название инструмента.
        """

        return self.__iid.name()

    def lot(self) -> int:
        """Return quantity of the one lot.

        # ru
        Возвращает название инструмента.
        """

        return self.__iid.lot()

    def step(self) -> float:
        """Return min price step.

        # ru
        Возвращает минимальный шаг цены.
        """
        return self.__iid.step()

    def path(self) -> Path:
        """Return dir path of instrument data.

        # ru
        Возвращает путь к папке с данными по этому инструменту.
        """
        return self.__iid.path()


class Share(Asset):
    """Aggregation of instrument id, charts, tics, footprint charts.

    # ru
    Акция - содержит идентификатор инструмента, графики разных таймфреймов
    и тиковые данные, а так же кластеры (footprint chart).

    Предоставляет интерфейс для доступа к данным по акции, загрузке графиков
    и тп.

    Перед обращение к графику Share.chart(...) его нужно загрузить.
    А перед обращением к кластерам Share.footprint(...) нужно загрузить тики
    и вызвать Share.build_footprint(...) для нужного таймфрейма.

    Графики сохраняются после загрузки.
    """

    def __init__(self, iid: Iid):
        Asset.__init__(self, iid)
        self.__charts: dict[TimeFrame, Chart] = dict()
        self.__tics = pl.DataFrame(schema=Tic.schema())
        self.__footprints: dict[TimeFrame, Footprint] = dict()

    @classmethod
    def from_str(self, iid_str: str) -> Any:
        """Create new share from str (case insensitive).

        # ru
        Создает акцию из строки (не чувствительно к регистру).
        Формат строки: "<exchange>_share_<ticker>".
        """

        iid = Manager.find(iid_str)
        assert iid.category() == Category.SHARE

        return Share(iid)

    @classmethod
    def from_csv(cls, csv_line: str) -> Any:
        """Create new share from csv.

        # ru
        Создает акцию из csv формата.
        Списки активов пользователя хранятся в csv файлах.
        """

        # line example: 'MOEX;SHARE;SBER;' or 'MOEX;SHARE;SBER'
        string = csv_line.strip().replace(";", "_")

        # MOEX_SHARE_SBER_ -> MOEX_SHARE_SBER
        if string.endswith("_"):
            string = string[0:-1]

        return Share.from_str(string)

    @classmethod
    def all(cls) -> list[Share]:
        """Return list with all shares whose have market data in user dir.

        # ru
        Возвращает список с акциями, для которых есть рыночные данные в
        папке пользователя.
        """

        shares: list[Share] = list()

        # shares dir path
        dir_path = CFG.Dir.data / "MOEX" / "SHARE"
        if not Cmd.is_exist(dir_path):
            raise FileNotFoundError("Data dir not found")

        # shares dirs: dir name == ticker
        dirs = Cmd.get_dirs(dir_path)
        if not dirs:
            log.warning(f"Shares not found! Dir empty: {dir_path}")
            return shares

        # create shares from dir name (ticker)
        for dir_path in dirs:
            dir_name = Cmd.name(dir_path)
            iid_str = f"MOEX_SHARE_{dir_name}"
            share = Share.from_str(iid_str)
            shares.append(share)

        return shares

    def chart(self, tf: TimeFrame) -> Chart | None:
        """Return chart.

        # ru
        Возвращает ссылку на график, или None если график заданного
        таймфрейма не загружен.

        """
        return self.__charts.get(tf)

    def load_chart(
        self,
        tf: TimeFrame,
        begin: DateTime | None = None,
        end: DateTime | None = None,
    ) -> Chart:
        """Load chart, return reference of loaded chart.

        # ru
        Загружает график.

        Если begin/end не указаны, то с количеством баров по умолчанию,
        которое задается в конфиге пользователя. Возвращает ссылку на
        загруженный график. График сохраняется внутри актива.
        """

        if begin is None or end is None:
            end = now()
            begin = end - tf.timedelta() * CFG.Core.default_bars_count

        chart = Chart.load(self.iid, tf, begin, end)
        self.__charts[tf] = chart

        return chart

    def load_chart_empty(self, tf) -> Chart:
        """Create empty chart with given timeframe, and store in self.

        # ru
        Создает пустой график для актива. Используется бэктестером.
        """
        chart = Chart.empty(self.iid, tf)
        self.__charts[tf] = chart

        return chart

    def tics(self) -> pl.DataFrame | None:
        """Return dataframe with tics data if loaded, else None.

        # ru
        Возвращает датафрейм тиков, если они загружены, иначе None.
        """

        if self.__tics.is_empty():
            return None

        return self.__tics

    def load_tics(self) -> pl.DataFrame:
        """Load tics data.

        # ru
        Загружает тиковые данные по активу.
        """

        end = now()
        begin = end - ONE_WEEK

        df = Manager.load(self.iid, MarketData.TIC, begin, end)
        self.__tics = df

        return df

    def bar_event(self, e: BarEvent) -> None:
        """Receive bar event

        # ru
        Принимает 'BarEvent', достает из него бар и добавляет во все имеющиеся
        графки. Графики сами разбираются в зависимости от своего таймфрейма
        как с этим баром 1М быть, автоматически склеивают все.

        Используется тестером и трейдером при получении нового бара из
        стрима данных.

        Не предназначена для прямого использования пользователем.
        """

        for _tf, chart in self.__charts.items():
            chart.add_bar(e.bar)

    def tic_event(self, e: TicEvent) -> None:
        """Receive tic event

        # ru
        Принимает 'TicEvent', сохраняет новый тик в активе. Используется
        тестером и трейдером при получении нового тика из стрима данных.
        Не предназначена для прямого использования пользователем.
        """

        self.__tics.extend(e.tic.df)

        for _tf, footprint in self.__footprints.items():
            footprint.add_tic(e.tic)


if __name__ == "__main__":
    ...
