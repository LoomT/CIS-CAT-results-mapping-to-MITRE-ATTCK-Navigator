import os
import sys
import pandas as pd

# Constants for mapping file
EX_MAP = 'CIS_Controls_v8_to_Enterprise_ATTCK_v82_Master_Mapping__5262021.xlsx'
SHEET_NAME = 'V8-ATT&CK Low (Sub-)Techniques'


# Load mapping once at import, convert to dicts for fast lookups
def _load_mapping_dicts(filename: str, sheet_name: str):
    if not os.path.exists(filename):
        filename = os.path.join('api', filename)
    df = pd.read_excel(filename, sheet_name=sheet_name, dtype=str).fillna('')
    safeguard_map: dict[str, list[str]] = {}
    control_map: dict[str, list[str]] = {}

    for _, row in df.iterrows():
        tech = row.get('Combined ATT&CK (Sub-)Technique ID') \
            or row.get('ATT&CK Technique ID')
        if not tech or pd.isna(tech):
            continue
        cis_safeguard = row.get('CIS Safeguard', '').strip()
        cis_control = row.get('CIS Control', '').strip()
        if cis_safeguard:
            safeguard_map.setdefault(cis_safeguard, []).append(tech)
        if cis_control:
            control_map.setdefault(cis_control, []).append(tech)

    return safeguard_map, control_map


_SAFEGUARD_MAP, _CONTROL_MAP = _load_mapping_dicts(EX_MAP, SHEET_NAME)
print("Mappings loaded in memory", file=sys.stderr, flush=True)


def gradient_color(score: float) -> str:
    s = max(0.0, min(1.0, score**2))

    if s == 1.0:
        return "#3bb143"  # hardcoded for score 1.0
    # define key colors
    r1, g1, b1 = 0xCC, 0x00, 0x00      # #CC0000 (red)
    r_mid, g_mid, b_mid = 0xFF, 0xD7, 0x00  # #FFD700 (golden yellow)
    r2, g2, b2 = 0x0B, 0xDA, 0x51      # #0bda51 (green)

    if s <= 0.5:
        t = s / 0.5
        r = int(r1 + (r_mid - r1) * t)
        g = int(g1 + (g_mid - g1) * t)
        b = int(b1 + (b_mid - b1) * t)
    else:
        t = (s - 0.5) / 0.5
        r = int(r_mid + (r2 - r_mid) * t)
        g = int(g_mid + (g2 - g_mid) * t)
        b = int(b_mid + (b2 - b_mid) * t)

    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def _accumulate_entries(
    entries: list[tuple[str, bool, str]],
    aggregator: dict[str, dict],
    include_comments: bool
) -> None:
    """
    Given a list of (techniqueID, passed_flag, comment_id) tuples,
    update aggregator counts and optionally comments.
    """
    for tech_id, passed_flag, comment_id in entries:
        entry = aggregator.setdefault(
            tech_id,
            {'pass': 0, 'total': 0, 'comments': []}
        )
        entry['total'] += 1
        if passed_flag:
            entry['pass'] += 1
        if include_comments:
            status = 'Pass' if passed_flag else 'Fail'
            entry['comments'].append(f"{comment_id} : {status}")


def _assemble_techniques(
    aggregator: dict[str, dict],
    include_comments: bool
) -> list[dict]:
    """
    Build the list of technique dicts from an aggregator mapping.
    If include_comments is False, 'comment' will be empty.
    """
    techniques: list[dict] = []
    for tech_id, data in aggregator.items():
        total = data['total']
        passed = data['pass']
        frac = passed / total if total else 0
        comment_text = "\n".join(data['comments']) if include_comments \
            else f'{passed}/{total}'
        techniques.append({
            'techniqueID': tech_id,
            'score': round(frac, 2),
            'color': gradient_color(frac),
            'comment': comment_text
        })
    return techniques


def generate_techniques(
    cis_data: dict,
    include_comments: bool = False
) -> list[dict]:
    """
    Aggregate CIS rule results into ATT&CK techniques,
    summarizing each test as "rule-id : Pass/Fail".
    Uses pre-loaded mapping dictionaries for lookups.
    Sub-techniques now also contribute to their parent technique.
    """
    aggregator: dict[str, dict] = {}
    raw_entries: list[tuple[str, bool, str]] = []

    for rule in cis_data.get('rules', []):
        rid = rule.get('rule-id', '')
        result = rule.get('result', '').lower()
        # ignore anything that isn’t exactly "pass" or "fail"
        if result not in ('pass', 'fail'):
            continue

        parts = rid.split('_')
        if len(parts) < 4:
            continue

        raw = parts[3]
        segs = raw.split('.')
        high = segs[0]
        low = '.'.join(segs[:2])

        # Find matching ATT&CK techniques by CIS Safeguard prefix
        matched_techs: set[str] = set()
        for sg_key, tech_list in _SAFEGUARD_MAP.items():
            if sg_key.startswith(low):
                matched_techs.update(tech_list)

        # If no safeguard match, try CIS Control exact match
        if not matched_techs:
            matched_techs.update(_CONTROL_MAP.get(high, []))

        # Ensure sub-techniques contribute to their parent technique
        parents = {t.split('.')[0] for t in matched_techs if '.' in t}
        matched_techs.update(parents)

        if not matched_techs:
            continue

        passed_flag = (result == 'pass')
        for tech in matched_techs:
            raw_entries.append((tech, passed_flag, rid))

    _accumulate_entries(raw_entries, aggregator, include_comments)
    return _assemble_techniques(aggregator, include_comments)


def build_layer(
    cis_data: dict,
    techniques: list[dict]
) -> dict:
    """
    Build the final Navigator layer JSON with header and techniques.
    """
    layer = {
        'version': '4.5.0',
        'name': cis_data.get(
            'benchmark-title',
            'MITRE ATT&CK NAVIGATOR LAYER'
        ),
        'domain': 'enterprise-attack',
        'description': 'Aggregated CIS findings mapped to MITRE ATT&CK',
        'techniques': techniques
    }
    print(f"Navigator layer with {len(techniques)} techniques generated")
    return layer


def convert_cis_to_attack(
    cis_data: dict,
    include_comments: bool = False
) -> dict:
    """
    Load mapping, generate techniques, and build the full Navigator layer.
    By default, comments are omitted.
    """
    techniques = generate_techniques(cis_data, include_comments)
    return build_layer(cis_data, techniques)


def combine_results(
    cis_data_list: list[dict],
    include_comments: bool = False
) -> dict:
    """
    Combine multiple CIS datasets at the rule level: if a rule fails in any,
    mark it as 'fail', otherwise 'pass'. Then run the normal CIS→ATT&CK
    conversion on the merged ruleset. Comments optional.
    """
    merged: dict[str, dict] = {}
    for cis in cis_data_list:
        for rule in cis.get('rules', []):
            rid = rule.get('rule-id')
            if not rid:
                continue
            result = rule.get('result', '').lower()
            # ignore anything that isn’t exactly "pass" or "fail"
            if result not in ('pass', 'fail'):
                continue
            if rid not in merged:
                merged[rid] = {
                    'rule-id': rid,
                    'rule-title': rule.get('rule-title', ''),
                    'result': result
                }
            else:
                if result == 'fail':
                    merged[rid]['result'] = 'fail'

    combined_cis = {
        'benchmark-title': 'Combined CIS Benchmark',
        'rules': list(merged.values())
    }

    return convert_cis_to_attack(combined_cis, include_comments)
