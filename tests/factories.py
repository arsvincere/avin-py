# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import polars as pl

from avin.domain.instrument.iid import Iid


def sber_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "exchange": ["MOEX"],
            "exchange_specific": ["moex_mrng_evng_e_wknd_dlr"],
            "category": ["SHARE"],
            "ticker": ["SBER"],
            "figi": ["BBG004730N88"],
            "country": ["RU"],
            "currency": ["rub"],
            "sector": ["financial"],
            "class_code": ["TQBR"],
            "isin": ["RU0009029540"],
            "uid": ["e6123145-9665-43e0-8413-cd61b8aa9b13"],
            "name": ["Сбер Банк"],
            "lot": ["1"],
            "step": ["0.01"],
            "long": ["0.1666"],
            "short": ["0.2"],
            "long_qual": ["0.125"],
            "short_qual": ["0.1428"],
            "first_1m": ["1520447580000000000"],
            "first_d": ["946969200000000000"],
        }
    )


def sber_iid() -> Iid:
    df = iid_cache_df()  # он из 1 строки, так что катит для создания Iid
    return Iid.from_df(df)
