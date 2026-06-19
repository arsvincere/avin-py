# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from pathlib import Path

__all__ = ("Cfg",)


class Cfg:
    class Dir:
        ROOT = Path.home() / "trading"
        DATA = ROOT / "data"
