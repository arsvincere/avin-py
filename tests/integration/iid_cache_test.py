# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest

from avin.domain.data.source import Source
from avin.domain.instrument.category import Category
from avin.storage.iid_storage import IidStorage
from avin.storage.tinkoff.source_tinkoff import SourceTinkoff


@pytest.fixture(autouse=True)
def clear_cache():
    IidStorage.load.cache_clear()
    IidStorage.find_code.cache_clear()
    IidStorage.find_figi.cache_clear()


# ----------------------------------------------------------------------------


@pytest.mark.integration
def test_tinkoff_cache_delete_save_load():
    source = Source.TINKOFF
    category = Category.SHARE

    IidStorage.delete(source, category)

    SourceTinkoff.cache()  # IidStorage.save(...) при это задействован

    df = IidStorage.load(source, category)

    assert not df.is_empty()


@pytest.mark.integration
def test_tinkoff_cache_find_code():
    code = "MOEX_SHARE_SBER"
    source = Source.TINKOFF

    iid = IidStorage.find_code(code, source)

    assert iid.ticker == "SBER"
    assert iid.figi == "BBG004730N88"
    assert iid.name == "Сбер Банк"


@pytest.mark.integration
def test_tinkoff_cache_find_figi():
    figi = "BBG004730N88"
    source = Source.TINKOFF

    iid = IidStorage.find_figi(figi, source)

    assert iid.ticker == "SBER"
    assert iid.figi == "BBG004730N88"
    assert iid.name == "Сбер Банк"
