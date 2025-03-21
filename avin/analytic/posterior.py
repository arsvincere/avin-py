#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import numpy as np
import polars as pl

from avin.analytic.trend import TrendAnalytic
from avin.core.chart import Chart
from avin.core.indicator import Indicator
from avin.core.timeframe import TimeFrame
from avin.extra.extremum_list import ExtremumList
from avin.extra.trend import Trend
from avin.utils import Signal


class PosteriorDelta(Indicator):
    name = "PosteriorDelta"

    def __init__(self):  # {{{
        """Posterior example  (pl.DataFrame)
        ┌───────┬─────────────┬────────────┬───────────┐
        │ delta ┆ probability ┆ cumulative ┆ price     │
        │ ---   ┆ ---         ┆ ---        ┆ ---       │
        │ f64   ┆ f64         ┆ f64        ┆ f64       │
        ╞═══════╪═════════════╪════════════╪═══════════╡
        │ 0.0   ┆ 1.0         ┆ 100.0      ┆ 19.415    │
        │ 0.1   ┆ 0.799779    ┆ 79.977886  ┆ 19.434415 │
        │ 0.2   ┆ 0.381815    ┆ 38.181509  ┆ 19.45383  │
        │ 0.3   ┆ 0.224717    ┆ 22.471719  ┆ 19.473245 │
        │ 0.4   ┆ 0.143914    ┆ 14.391426  ┆ 19.49266  │
        │ …     ┆ …           ┆ …          ┆ …         │
        """
        # data
        self.__schema = {
            "delta": float,
            "probability": float,
            "cumulative": float,
            "price": float,
        }

        # signals
        self.upd_posterior = Signal(Trend, pl.DataFrame)
        self.new_posterior = Signal(Trend, pl.DataFrame)

    # }}}

    @property  # asset   # {{{
    def asset(self) -> Asset:
        return self.__chart.asset

    # }}}
    @property  # chart  # {{{
    def chart(self) -> Chart:
        return self.__chart

    # }}}
    @property  # timeframe # {{{
    def timeframe(self) -> TimeFrame:
        return self.__chart.timeframe

    # }}}

    def setChart(self, chart: Chart) -> None:  # {{{
        self.__chart = chart

        # для работы индикаторы необходим индикатор ExtremumList на графике
        # проверяем его наличие, или добавляем на график если нет
        elist = self.__chart.getInd(ExtremumList.name)
        if elist is None:
            elist = ExtremumList()
            self.__chart.addInd(elist)
        self.__elist = elist

        # connect
        self.__elist.upd_trend.connect(self.__onRealTimeTrend)
        self.__elist.new_trend.connect(self.__onHistoricalTrend)

    # }}}
    def last(self, term: Term) -> (Trend, pl.DataFrame):  # {{{
        last_trend = self.__elist.trend(term, 1)
        step = self.defaultStep(last_trend)
        p = self.posteriorStep(last_trend, step)
        return last_trend, p

    # }}}
    def now(self, term: Term) -> (Trend, pl.DataFrame):  # {{{
        now_trend = self.__elist.trend(term, 0)
        step = self.defaultStep(now_trend)
        p = self.posteriorStep(now_trend, step)
        return now_trend, p

    # }}}
    def posteriorSize(self, trend: Trend) -> pl.DataFrame | None:  # {{{
        assert isinstance(trend, Trend)

        # try get trend delta size
        size = TrendAnalytic.deltaSize(trend)
        if size is None:
            return None

        # get df with cumulative probability
        trait = "delta_size"
        H = [str(i) for i in Size]
        obs = str(size)
        trends = TrendAnalytic.load(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            analyse=TrendAnalytic.Analyse.TREND,
        )
        posterior = self.__posterior(obs, H, trait, trends)

        # load sizes table
        sizes = TrendAnalytic.load(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            analyse=TrendAnalytic.Analyse.SIZE,
        )
        trait_sizes = sizes.filter(pl.col("trait") == "delta")

        # Если тренд бычий, значит следующий медвежий.
        # а дельты все по модулю посчитаны, так что
        # для определения цен текущего медвежьего тренда, надо
        # дельты умножить на -1
        if trend.isBull():
            trait_sizes = trait_sizes.with_columns(
                begin=-pl.col("begin"),
                end=-pl.col("end"),
            )

        # calc prices
        price = trend.end.price
        posterior = posterior.with_columns(
            begin_price=price + trait_sizes["begin"] * price / 100,
            end_price=price + trait_sizes["end"] * price / 100,
        )

        return posterior

    # }}}
    def posteriorSimpleSize(self, trend: Trend) -> pl.DataFrame | None:  # {{{
        assert isinstance(trend, Trend)

        # try get trend delta size
        size = TrendAnalytic.deltaSize(trend)
        if size is None:
            return None

        # get df with cumulative probability
        trait = "delta_ssize"
        H = [str(i) for i in SimpleSize]
        obs = str(size.simple())
        trends = TrendAnalytic.load(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            analyse=TrendAnalytic.Analyse.TREND,
        )
        posterior = self.__posterior(obs, H, trait, trends)

        # load sizes table
        ssizes = TrendAnalytic.load(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            analyse=TrendAnalytic.Analyse.SIMPLE_SIZE,
        )
        trait_ssizes = ssizes.filter(pl.col("trait") == "delta")

        # Если тренд бычий, значит следующий медвежий.
        # а дельты все по модулю посчитаны, так что
        # для определения цен текущего медвежьего тренда, надо
        # дельты умножить на -1
        if trend.isBull():
            trait_ssizes = trait_ssizes.with_columns(
                begin=-pl.col("begin"),
                end=-pl.col("end"),
            )

        # calc prices
        price = trend.end.price
        posterior = posterior.with_columns(
            # begin_price=price,  # + trait_ssizes["begin"] * price / 100,
            begin_price=price + trait_ssizes["begin"] * price / 100,
            end_price=price + trait_ssizes["end"] * price / 100,
        )

        return posterior

    # }}}
    def posteriorStep(  # {{{
        self, trend: Trend, step: float
    ) -> pl.DataFrame | None:
        assert isinstance(trend, Trend)

        # try get trend delta size
        size = TrendAnalytic.deltaSize(trend)
        if size is None:
            return None

        # get df with cumulative probability
        obs = {
            "feat": "delta_size",
            "value": str(size),
        }
        trends = TrendAnalytic.load(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            analyse=TrendAnalytic.Analyse.TREND,
        )
        posterior = self.__calcPosteriorStep(obs, step, trends)

        # Если тренд бычий, значит следующий медвежий.
        # а дельты все по модулю посчитаны, так что
        # для определения цен текущего медвежьего тренда, надо
        # дельты умножить на -1
        k = -1 if trend.isBull() else 1

        # calc prices
        price = trend.end.price
        posterior = posterior.with_columns(
            price=price + k * posterior["delta"] * price / 100,
        )

        return posterior

    # }}}
    def defaultStep(self, trend: Trend) -> float:  # {{{
        match str(trend.timeframe):
            case "1M":
                step = 0.05
            case "5M":
                step = 0.1
            case "1H":
                step = 0.2
            case "D":
                step = 1.0
            case "W":
                step = 2.0
            case "M":
                step = 3.0
            case _:
                assert False, "TODO_ME"

        return step

    # }}}

    def __calcPosteriorSize(  # {{{
        self, obs: str, H: list[str], trait: str, trends: pl.DataFrame
    ) -> pl.DataFrame:
        df = trends.with_row_index()
        obs_trends = df.filter(pl.col(trait) == obs)
        obs_index = obs_trends["index"]
        h_index = obs_index + 1

        posterior = list()
        for h in H:
            pair_trends = df.filter(
                pl.col("index").is_in(h_index),
                pl.col(trait) == h,
            )
            p = len(pair_trends) / len(obs_trends)
            posterior.append(p)

        result = pl.DataFrame(
            {
                trait: H,
                "probability": posterior,
            }
        )
        result = result.with_columns(
            cumulative=pl.col("probability").reverse().cum_sum().reverse()
            * 100
        )
        return result

    # }}}
    def __calcPosteriorStep(  # {{{
        self, obs: dict, step: float, trends: pl.DataFrame
    ) -> pl.DataFrame:
        df = trends.with_row_index()
        obs_trends = df.filter(pl.col(obs["feat"]) == obs["value"])
        obs_index = obs_trends["index"]
        h_index = obs_index + 1

        begin = 0
        end = trends["delta"].max() + step

        delta = list()
        posterior = list()
        X = np.arange(begin, end, step)
        for x in X:
            combo = df.filter(
                pl.col("index").is_in(h_index),
                pl.col("delta") > x,
            )
            p = len(combo) / len(obs_trends)

            delta.append(x)
            posterior.append(p)

            if p <= 0.01:
                break

        result = pl.DataFrame(
            {
                "delta": delta,
                "probability": posterior,
            }
        )
        result = result.with_columns(
            cumulative=pl.col("probability") * 100,
        )
        return result

    # }}}

    def __onRealTimeTrend(self, trend: Trend):  # {{{
        step = self.defaultStep(trend)
        posterior = self.posteriorStep(trend, step)

        self.upd_posterior.emit(trend, posterior)

    # }}}
    def __onHistoricalTrend(self, trend: Trend):  # {{{
        step = self.defaultStep(trend)
        posterior = self.posteriorStep(trend, step)

        self.new_posterior.emit(trend, posterior)

    # }}}


if __name__ == "__main__":
    ...
