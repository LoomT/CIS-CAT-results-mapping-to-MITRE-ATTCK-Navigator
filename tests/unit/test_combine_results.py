import json
import sys
import time
# noqa: E402
sys.path.insert(0, './api')

from convert import combine_results, convert_cis_to_attack  # noqa: E402


def compare_layer_scores(live_layer: dict, known_path: str):
    """
    Compare live converted data against a known-good JSON file.
    Returns mismatches(techniqueID, live_score, known_score).
    """
    with open(known_path, 'r', encoding='utf-8') as f:
        known_layer = json.load(f)

    live_scores = {t['techniqueID']: t['score']
                   for t in live_layer.get('techniques', [])}
    known_scores = {t['techniqueID']: t['score']
                    for t in known_layer.get('techniques', [])}

    mismatches = []
    all_ids = set(live_scores) | set(known_scores)
    for tid in sorted(all_ids):
        ls = live_scores.get(tid)
        ks = known_scores.get(tid)
        if ls != ks:
            mismatches.append((tid, ls, ks))
    return mismatches


def test_all_entries_fail():
    """
    Combine two CIS inputs (one all-fail, one all-pass)
    and assert every technique ends up failing.
    """
    base = './tests/data'
    cis_fail = json.load(open(f"{base}/cisinput-false.json", encoding="utf-8"))
    cis_pass = json.load(open(f"{base}/cisinput-true.json", encoding="utf-8"))

    layer = combine_results([cis_fail, cis_pass])
    techniques = layer.get('techniques', [])
    assert techniques, "No techniques generated"

    # all scores should be zero (i.e. Fail)
    assert all(t['score'] == 0.0 for t in techniques)


def test_host_nonpassing_conversion():
    """
    Convert the non‑passing host CIS input and compare scores
    against the known output.
    """
    input_path = "tests/data/host-CIS_input-20250101T000000Z-NonPassing.json"
    known_path = "tests/data/host-MITRE-20250101T000000Z-NonPassing.json"

    cis = json.load(open(input_path, encoding="utf-8"))
    live_layer = convert_cis_to_attack(cis)

    diffs = compare_layer_scores(live_layer, known_path)
    assert not diffs, f"Found score mismatches:\n{diffs}"


def test_library_load_time():
    """
    Ensure that importing the conversion library takes no more than 2 seconds.
    """
    # Remove from cache to measure actual import cost
    sys.modules.pop('convert', None)
    start = time.perf_counter()
    import convert  # noqa: F401
    elapsed = time.perf_counter() - start
    assert elapsed <= 2.0, f"Library load took {elapsed:.2f}s, exceeds 2s"


def test_conversion_performance():
    """
    Ensure that converting a CIS dataset takes no more than 0.5 seconds.
    """
    input_path = "tests/data/host-CIS_input-20250101T000000Z-NonPassing.json"
    cis = json.load(open(input_path, encoding="utf-8"))
    # Warm-up run
    _ = convert_cis_to_attack(cis)
    start = time.perf_counter()
    _ = convert_cis_to_attack(cis)
    elapsed = time.perf_counter() - start
    assert elapsed <= 0.5, f"Conversion took {elapsed:.2f}s, exceeds 0.5s"
