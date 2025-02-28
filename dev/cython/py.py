#!/usr/bin/env  python3


def test(x):
    y = 1
    for i in range(1, x + 1):
        y *= i
    return y


# import asyncio
#
# from avin import *
#
#
# async def main():
#     # ids = await Data.find(AssetType.SHARE, Exchange.MOEX, "MVID")
#     # ID = ids[0]
#
#     # await Data.download(DataSource.MOEX, DataType.BAR_1M, ID, 2023)
#     # await Data.download(DataSource.MOEX, DataType.BAR_1M, ID, 2024)
#     # await Data.download(DataSource.MOEX, DataType.BAR_1H, ID, 2023)
#     # await Data.download(DataSource.MOEX, DataType.BAR_1H, ID, 2024)
#     # await Data.download(DataSource.MOEX, DataType.BAR_D, ID, 2023)
#     # await Data.download(DataSource.MOEX, DataType.BAR_D, ID, 2024)
#
#     await Data.updateAll()
#
#     ID = await InstrumentId.byTicker(AssetType.SHARE, Exchange.MOEX, "AFKS")
#     await Data.convert(ID, DataType.BAR_1M, DataType.BAR_5M)
#     ID = await InstrumentId.byTicker(AssetType.SHARE, Exchange.MOEX, "AFLT")
#     await Data.convert(ID, DataType.BAR_1M, DataType.BAR_5M)
#     ID = await InstrumentId.byTicker(AssetType.SHARE, Exchange.MOEX, "ALRS")
#     await Data.convert(ID, DataType.BAR_1M, DataType.BAR_5M)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
