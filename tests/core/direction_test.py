# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_direction_buy():
    value = 123456.99
    direction = Direction.Buy

    assert direction.name == "Buy"
    assert value * direction.value == value


def test_direction_sell():
    value = 123456.99
    direction = Direction.Sell

    assert direction.name == "Sell"
    assert value * direction.value == value * -1
