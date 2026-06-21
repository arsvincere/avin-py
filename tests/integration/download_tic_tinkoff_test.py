import pytest

from avin import *


@pytest.mark.integration
def test_download_tic_tinkoff():
    sber = AssetFactory.new("MOEX_SHARE_SBER")

    SourceTinkoff.download(sber.iid(), MarketData.TIC, 2026)
