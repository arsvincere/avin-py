#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from avin.analytic._analytic import Analytic
from avin.analytic.bar import BarAnalytic
from avin.analytic.posterior import PosteriorDelta
from avin.analytic.tic_hist import Hist
from avin.analytic.trend import TrendAnalytic
from avin.analytic.vawe import VaweAnalytic
from avin.analytic.volume import VolumeAnalytic

__all__ = (
    "Analytic",
    "BarAnalytic",
    "Hist",
    "PosteriorDelta",
    "TrendAnalytic",
    "VaweAnalytic",
    "VolumeAnalytic",
)
