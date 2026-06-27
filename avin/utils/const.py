# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from datetime import UTC
from datetime import time as Time
from datetime import timedelta as TimeDelta

ONE_SECOND = TimeDelta(seconds=1)
ONE_MINUTE = TimeDelta(minutes=1)
FIVE_MINUTE = TimeDelta(minutes=5)
TEN_MINUTE = TimeDelta(minutes=10)
ONE_HOUR = TimeDelta(hours=1)
ONE_DAY = TimeDelta(days=1)
ONE_WEEK = TimeDelta(weeks=1)
ONE_MONTH = TimeDelta(days=30)
ONE_YEAR = TimeDelta(days=365)

DAY_BEGIN = Time(0, 0, tzinfo=UTC)
DAY_END = Time(23, 59, tzinfo=UTC)
