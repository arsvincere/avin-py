import pytest

from avin import *


@pytest.mark.integration
def test_download_bar_tinkoff():
    sber = AssetFactory.new("MOEX_SHARE_SBER")

    SourceTinkoff.download(sber.iid(), MarketData.BAR_1M, 2026)
