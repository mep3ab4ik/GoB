import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _flush_db():
    cache.clear()
