import pytest

from avin import *


@pytest.mark.integration
def test_tinkoff_cache():
    SourceTinkoff.cache()
