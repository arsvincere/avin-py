# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_new():
    price = 321.2
    q = Quant(price)

    assert q.price == price
    assert q.vol() == 0
    assert q.vol_s == 0
    assert q.vol_b == 0
    assert q.val() == 0.0
    assert q.val_s == 0.0
    assert q.val_b == 0.0


def test_add():
    price = 321.25
    q = Quant(price)

    tic = Tic.new(100500, Direction.BUY, 1, 321.25, 3212.5, 1, 654654654)
    q.add(tic)
    assert q.price == price
    assert q.vol() == 1
    assert q.vol_s == 0
    assert q.vol_b == 1
    assert q.val() == 3212.5
    assert q.val_s == 0.0
    assert q.val_b == 3212.5

    tic = Tic.new(100500, Direction.SELL, 2, 321.25, 3212.5 * 2, 1, 654654654)
    q.add(tic)
    assert q.price == price
    assert q.vol() == 3
    assert q.vol_s == 2
    assert q.vol_b == 1
    assert q.val() == 3212.5 * 3
    assert q.val_s == 3212.5 * 2
    assert q.val_b == 3212.5
