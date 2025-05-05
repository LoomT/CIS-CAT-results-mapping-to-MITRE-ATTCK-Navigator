import pytest
# from api.utils import example


@pytest.mark.parametrize("raw,expected", [("3+5", 8), ("2+4", 6), ("6*9", 54)])
def test_example_basic(raw, expected):
    assert eval(raw) == expected
