import json
import sys
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


def test_single_input_all_pass():
    """
    Single CIS input with all-pass => every score 1.0, no comments.
    """
    base = './tests/data'
    cis_true = json.load(
        open(f"{base}/cisinput-true.json", 'r', encoding='utf-8')
    )
    layer = combine_results([cis_true])
    techs = layer.get('techniques', [])
    assert techs, "No techniques generated"
    assert all(t['score'] == 1.0 for t in techs)


def test_layer_schema():
    """
    Output dict and techniques entries match expected schema.
    """
    base = './tests/data'
    cis_true = json.load(
        open(f"{base}/cisinput-true.json", 'r', encoding='utf-8')
    )
    layer = convert_cis_to_attack(cis_true)
    keys = set(layer.keys())
    assert keys == {'version', 'name', 'domain', 'description',
                    'techniques'}
    for t in layer['techniques']:
        tkeys = set(t.keys())
        assert tkeys == {'techniqueID', 'score', 'color',
                         'comment'}


def test_combine_idempotent():
    """
    combine_results twice yields identical output.
    """
    base = './tests/data'
    cis_false = json.load(
        open(f"{base}/cisinput-false.json", 'r', encoding='utf-8')
    )
    cis_true = json.load(
        open(f"{base}/cisinput-true.json", 'r', encoding='utf-8')
    )
    inp = [cis_false, cis_true]
    out1 = combine_results(inp)
    out2 = combine_results(inp)
    assert out1 == out2, "combine_results is not idempotent"


def test_ordering_invariance():
    """
    Shuffling input rules does not change sorted techniques.
    """
    path = (
        "tests/data/host-CIS_input-20250101T000000Z-"
        "NonPassing.json"
    )
    cis = json.load(open(path, 'r', encoding='utf-8'))
    # shuffle rules
    import random
    rules = cis.get('rules', [])[:]
    random.shuffle(rules)
    cis_shuf = dict(cis)
    cis_shuf['rules'] = rules
    out_orig = convert_cis_to_attack(cis)
    out_shuf = convert_cis_to_attack(cis_shuf)
    ids1 = sorted(t['techniqueID']
                  for t in out_orig['techniques'])
    ids2 = sorted(t['techniqueID']
                  for t in out_shuf['techniques'])
    assert ids1 == ids2, "Ordering affects output IDs"
