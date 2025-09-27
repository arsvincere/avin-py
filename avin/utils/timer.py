# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import time


class Timer:
    __START = 0.0
    __FINISH = 0.0

    @staticmethod
    def start():
        Timer.__START = time.time()

    @staticmethod
    def finish(msg: str = ""):
        Timer.__FINISH = time.time()
        t = Timer.__FINISH - Timer.__START
        print(f":: Timer {msg} - {t:.6f}")


if __name__ == "__main__":
    ...
