import pytest

from pipelines.common.spark import get_spark


@pytest.fixture(scope="session")
def spark():
    s = get_spark("tests", delta=False)  # transforms are tested without Delta
    yield s
    s.stop()
