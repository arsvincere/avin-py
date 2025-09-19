# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================


from avin import *


def test_asset_list():
    asset_list = AssetList("MyList")

    assert asset_list.name == "MyList"
    assert len(asset_list) == 0
    assert asset_list.is_empty()


def test_load():
    asset_list = AssetList.load("xxx")

    assert asset_list.name == "xxx"
    assert len(asset_list) == 20
    assert not asset_list.is_empty()

    for i in asset_list:
        assert isinstance(i, Asset)

    assert asset_list[0].ticker() == Ticker("AFKS")


def test_find():
    asset_list = AssetList.load("xxx")

    sber = asset_list.find_figi("BBG004730N88")
    assert sber.ticker() == Ticker("SBER")
