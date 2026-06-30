# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from avin.domain.asset.base_asset import BaseAsset
from avin.domain.chart.chart import Chart
from avin.domain.common.timeframe import TimeFrame
from avin.domain.data.source import Source
from avin.domain.footprint.tick_footprint import TickFootprint
from avin.domain.footprint.time_footprint import TimeFootprint
from avin.domain.footprint.value_footprint import ValueFootprint
from avin.domain.footprint.volume_footprint import VolumeFootprint
from avin.domain.raw.tick import Tick
from avin.storage.bar_storage import BarStorage
from avin.storage.codec import StorageCodec
from avin.system.conf import cfg
from avin.utils.dt import DateTime, dt_to_ts, ts_to_dt


class Loader:
    """
    Public market-data loader.

    -- ru
    Публичный загрузчик market data.
    """

    @staticmethod
    def chart(
        asset: BaseAsset,
        tf: TimeFrame,
        source: Source | None = None,
        bars_count: int | None = None,
        force: bool = False,
    ) -> Chart:
        """
        Load default chart.

        -- ru
        Загрузить график по умолчанию.
        """
        source = _source(source)
        bars_count = _bars_count(bars_count)

        if not force and asset.has_chart(tf):
            chart = asset.chart(tf)
            if len(chart) >= bars_count:
                return chart

        return _load_chart(asset, tf, source, bars_count)

    @staticmethod
    def chart_period(
        asset: BaseAsset,
        tf: TimeFrame,
        begin: DateTime,
        end: DateTime,
        source: Source | None = None,
        force: bool = False,
    ) -> Chart:
        """
        Load chart for [begin, end) period.

        -- ru
        Загрузить график за период [begin, end).
        """
        raise NotImplementedError

    @staticmethod
    def ticks(
        asset: BaseAsset,
        source: Source | None = None,
        force: bool = False,
    ) -> list[Tick]:
        """
        Load default ticks.

        -- ru
        Загрузить ticks по умолчанию.
        """
        raise NotImplementedError

    @staticmethod
    def ticks_period(
        asset: BaseAsset,
        begin: DateTime,
        end: DateTime,
        source: Source | None = None,
        force: bool = False,
    ) -> list[Tick]:
        """
        Load ticks for [begin, end) period.

        -- ru
        Загрузить ticks за период [begin, end).
        """
        raise NotImplementedError

    @staticmethod
    def time_footprint(
        asset: BaseAsset,
        tf: TimeFrame,
        source: Source | None = None,
        force: bool = False,
    ) -> TimeFootprint:
        """
        Load default time footprint.

        -- ru
        Загрузить time footprint по умолчанию.
        """
        raise NotImplementedError

    @staticmethod
    def time_footprint_period(
        asset: BaseAsset,
        tf: TimeFrame,
        begin: DateTime,
        end: DateTime,
        source: Source | None = None,
        force: bool = False,
    ) -> TimeFootprint:
        """
        Load time footprint for [begin, end) period.

        -- ru
        Загрузить time footprint за период [begin, end).
        """
        raise NotImplementedError

    @staticmethod
    def tick_footprint(
        asset: BaseAsset,
        ticks_per_cluster: int,
        source: Source | None = None,
        force: bool = False,
    ) -> TickFootprint:
        """
        Load default tick footprint.

        -- ru
        Загрузить tick footprint по умолчанию.
        """
        raise NotImplementedError

    @staticmethod
    def tick_footprint_period(
        asset: BaseAsset,
        ticks_per_cluster: int,
        begin: DateTime,
        end: DateTime,
        source: Source | None = None,
        force: bool = False,
    ) -> TickFootprint:
        """
        Load tick footprint for [begin, end) period.

        -- ru
        Загрузить tick footprint за период [begin, end).
        """
        raise NotImplementedError

    @staticmethod
    def volume_footprint(
        asset: BaseAsset,
        volume_per_cluster: int,
        source: Source | None = None,
        force: bool = False,
    ) -> VolumeFootprint:
        """
        Load default volume footprint.

        -- ru
        Загрузить volume footprint по умолчанию.
        """
        raise NotImplementedError

    @staticmethod
    def volume_footprint_period(
        asset: BaseAsset,
        volume_per_cluster: int,
        begin: DateTime,
        end: DateTime,
        source: Source | None = None,
        force: bool = False,
    ) -> VolumeFootprint:
        """
        Load volume footprint for [begin, end) period.

        -- ru
        Загрузить volume footprint за период [begin, end).
        """
        raise NotImplementedError

    @staticmethod
    def value_footprint(
        asset: BaseAsset,
        value_per_cluster: float,
        source: Source | None = None,
        force: bool = False,
    ) -> ValueFootprint:
        """
        Load default value footprint.

        -- ru
        Загрузить value footprint по умолчанию.
        """
        raise NotImplementedError

    @staticmethod
    def value_footprint_period(
        asset: BaseAsset,
        value_per_cluster: float,
        begin: DateTime,
        end: DateTime,
        source: Source | None = None,
        force: bool = False,
    ) -> ValueFootprint:
        """
        Load value footprint for [begin, end) period.

        -- ru
        Загрузить value footprint за период [begin, end).
        """
        raise NotImplementedError


def _source(source: Source | None) -> Source:
    return source or cfg.default_source


def _bars_count(bars_count: int | None) -> int:
    count = cfg.default_bars_count if bars_count is None else bars_count

    if count <= 0:
        raise ValueError("bars_count must be positive")

    return count


def _load_chart(
    asset: BaseAsset,
    tf: TimeFrame,
    source: Source,
    bars_count: int,
) -> Chart:
    md = tf.to_market_data()
    last_df = BarStorage.load_last(asset.iid, source, md)
    last_ts = last_df.item(-1, "ts")

    end = ts_to_dt(tf.end_frame_ts(last_ts))
    begin = end - tf.timedelta * bars_count

    return _load_chart_period(asset, tf, begin, end, source)


def _chart_for_period(
    asset: BaseAsset,
    tf: TimeFrame,
    begin: DateTime,
    end: DateTime,
    source: Source,
    force: bool,
) -> Chart:
    if not force and asset.has_chart(tf):
        chart = asset.chart(tf)
        if _chart_naively_covers(chart, begin, end):
            return chart

    return _load_chart_period(asset, tf, begin, end, source)


def _load_chart_period(
    asset: BaseAsset,
    tf: TimeFrame,
    begin: DateTime,
    end: DateTime,
    source: Source,
) -> Chart:
    md = tf.to_market_data()
    df = BarStorage.load_range(asset.iid, source, md, begin, end)
    bars = StorageCodec.bars_from_df(df)

    chart = Chart(asset.iid, tf, bars)
    asset._set_chart(chart)

    return chart


def _chart_naively_covers(
    chart: Chart,
    begin: DateTime,
    end: DateTime,
) -> bool:
    """
    Naive coverage check for current Loader stage.

    This check looks only at existing bar timestamps. It may return False
    for valid exchange-session gaps, weekends, clearing breaks or early
    closes. In that case Loader reloads chart "just in case".

    Strict coverage should later use loaded range metadata, not first/current
    bar timestamps.

    -- ru
    Наивная проверка покрытия для текущей стадии Loader.

    Проверка смотрит только на timestamp-ы существующих баров. Она может
    вернуть False на валидных дырках торговой сессии, выходных, клиринге
    или раннем закрытии. В этом случае Loader перезагружает chart
    "на всякий случай".

    Строгое покрытие позже должно проверяться по metadata загруженного
    диапазона, а не по first/current timestamp-ам баров.
    """
    first = chart.first
    current = chart.current

    if first is None or current is None:
        return False

    begin_ts = dt_to_ts(begin)
    end_ts = dt_to_ts(end)

    return first.ts <= begin_ts and current.ts >= end_ts
