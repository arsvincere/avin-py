# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_log():
    log.debug("Debug test")
    log.info("Info test")
    log.warning("Warning test")
    log.error("Error test")
    log.critical("Critical test")
