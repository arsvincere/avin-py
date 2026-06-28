# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest
from avin.domain.common.direction import Direction
from avin.domain.footprint.cluster import Cluster
from avin.domain.footprint.ladder import Ladder
from avin.domain.footprint.level import Level
from avin.domain.raw.tick import Tick


@pytest.mark.smoke
def test_tick_level_ladder_cluster_smoke() -> None:
    buy_tick = Tick(
        ts=1_700_000_000_000_000_000,
        direction=Direction.BUY,
        price=100.0,
        lots=10,
        quantity=10,
        value=1_000.0,
    )

    sell_tick = Tick(
        ts=1_700_000_000_100_000_000,
        direction=Direction.SELL,
        price=100.0,
        lots=4,
        quantity=4,
        value=400.0,
    )

    level = Level(price=100.0)
    level.add(buy_tick)
    level.add(sell_tick)

    assert level.price == 100.0
    assert level.vol_b == 10
    assert level.vol_s == 4
    assert level.vol == 14
    assert level.delta_vol == 6
    assert level.trades == 2

    ladder = Ladder()
    ladder.add(buy_tick)
    ladder.add(sell_tick)

    assert len(ladder) == 1
    assert 100.0 in ladder
    assert ladder.high == 100.0
    assert ladder.low == 100.0

    cluster = Cluster()
    cluster.add(buy_tick)
    cluster.add(sell_tick)

    assert cluster.open == 100.0
    assert cluster.high == 100.0
    assert cluster.low == 100.0
    assert cluster.close == 100.0
    assert cluster.vol == 14
    assert cluster.val == 1_400.0
    assert cluster.trades == 2
