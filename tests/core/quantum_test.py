# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from pathlib import Path

from avin import *


def test_quantum():
    path = Path(
        "/home/alex/avin/usr/data/MOEX/SHARE/AFKS/TIC/2025/2025-09-16.parquet"
    )

    tics = Cmd.read_pqt(path)
    tics = tics.tail(10)

    quantum = Quantum(tics)
    count = len(quantum.quants)
    assert count == 6
