import json
import pytest
import sys
# noqa: E402
sys.path.insert(0, './api')
from convert import combine_results  # noqa: E402


@pytest.fixture
def cis_inputs():
    base = './tests'
    return [
        json.load(open(f"{base}/cisinput-false.json")),
        json.load(open(f"{base}/cisinput-true.json")),
    ]


def test_all_entries_fail(cis_inputs):
    """
    Combine the two CIS inputs and assert every technique ends up failing.
    """
    layer = combine_results(cis_inputs)
    techniques = layer.get('techniques', [])
    # there should be at least one technique
    assert techniques, "No techniques generated"
    # all scores should be zero (i.e. Fail)
    assert all(t['score'] == 0.0 for t in techniques)
    # and each comment line should end with "Fail"
    for t in techniques:
        for line in t['comment'].splitlines():
            assert line.strip().endswith('Fail')
