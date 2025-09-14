# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from pathlib import Path

__all__ = ("CFG",)


class CFG:
    class Dir:
        """Program directories"""

        # Specify absolute path to program dir
        root = Path.home() / "avin"

        # All user files by default in the 'root/usr', you can specify
        # an absolute path to another location. All user data be there.
        usr = root / "usr"

        # User data
        data = usr / "data"
        log = usr / "log"

        # Resources - don't edit it
        icon = root / "res" / "icon"

    class Connect:
        pass

    class Usr:
        pass

    class Log:
        history = 5
        debug = True
        info = True

    class Data:
        pass

    class Core:
        pass

    class Tester:
        pass

    class Trader:
        pass

    class Terminal:
        pass

    class Gui:
        pass
