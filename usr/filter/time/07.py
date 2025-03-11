from avin import *


async def conditionChart(chart: Chart) -> bool:
    assert chart.timeframe == TimeFrame("5M")

    if chart.now.dt.time().hour != 7:
        return False

    return True


async def conditionAsset(asset: Asset) -> bool:
    chart = asset.chart("5M")
    result = await conditionChart(chart)
    return result


async def conditionTrade(trade: Trade) -> bool:
    # грузим график
    timeframe = TimeFrame("5M")
    if trade.status == Trade.Status.CLOSED:
        end = trade.openDateTime()
    else:
        end = trade.dt
    begin = end - 3 * timeframe  # 3 бара тут более чем достаточно))
    chart = await Chart.load(trade.instrument, timeframe, begin, end)
    chart.setHeadDatetime(end)

    result = await conditionChart(chart)
    return result
