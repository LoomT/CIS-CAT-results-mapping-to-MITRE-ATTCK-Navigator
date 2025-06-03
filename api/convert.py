import os
import pandas as pd

# Constants for mapping file
EX_MAP = 'CIS_Controls_v8_to_Enterprise_ATTCK_v82_Master_Mapping__5262021.xlsx'
SHEET_NAME = 'V8-ATT&CK Low (Sub-)Techniques'


def load_mapping(filename: str, sheet_name: str) -> pd.DataFrame:
    """
    Load the CIS-to-ATT&CK mapping Excel sheet, adding 'api/' prefix if needed.
    """
    if not os.path.exists(filename):
        filename = os.path.join('api', filename)
    return pd.read_excel(filename, sheet_name=sheet_name, dtype=str)


def gradient_color(fraction: float) -> str:
    """
    Compute an orange-to-green gradient color for a given fraction [0,1].
    """
    if fraction <= 0.5:
        ratio = fraction / 0.5
        r = 255
        g = int(153 * ratio)
        b = 51
    else:
        ratio = (fraction - 0.5) / 0.5
        r = int(255 - 204 * ratio)
        g = int(153 + 51 * ratio)
        b = 51
    return f"#{r:02x}{g:02x}{b:02x}"


def _accumulate_entries(
    entries: list[tuple[str, bool, str]],
    aggregator: dict[str, dict]
) -> None:
    """
    Given a list of (techniqueID, passed_flag, comment_id) tuples,
    update aggregator counts and comments. comment_id is what gets printed
    before the “: Pass/Fail”.
    """
    for tech_id, passed_flag, comment_id in entries:
        entry = aggregator.setdefault(
            tech_id,
            {'pass': 0, 'total': 0, 'comments': []}
        )
        entry['total'] += 1
        if passed_flag:
            entry['pass'] += 1
        status = 'Pass' if passed_flag else 'Fail'
        entry['comments'].append(f"{comment_id} : {status}")


def _assemble_techniques(
    aggregator: dict[str, dict]
) -> list[dict]:
    """
    Build the list of technique dicts from an aggregator mapping.
    """
    techniques: list[dict] = []
    for tech_id, data in aggregator.items():
        total = data['total']
        passed = data['pass']
        frac = passed / total if total else 0
        techniques.append({
            'techniqueID': tech_id,
            'score': round(frac, 2),
            'color': gradient_color(frac),
            'comment': "\n".join(data['comments'])
        })
    return techniques


def generate_techniques(cis_data: dict, df: pd.DataFrame) -> list[dict]:
    """
    Aggregate CIS rule results into ATT&CK techniques,
    summarizing each test as "rule-id : Pass/Fail".
    """
    aggregator: dict[str, dict] = {}
    raw_entries: list[tuple[str, bool, str]] = []

    for rule in cis_data.get('rules', []):
        rid = rule.get('rule-id', '')
        result = rule.get('result', '').lower()
        parts = rid.split('_')
        if len(parts) < 4:
            continue

        raw = parts[3]
        segs = raw.split('.')
        high = segs[0]
        low = '.'.join(segs[:2])

        matches = df[df['CIS Safeguard'].fillna('').str.startswith(low)]
        if matches.empty:
            matches = df[df['CIS Control'] == high]

        passed_flag = (result != 'fail')
        for _, row in matches.iterrows():
            tech = (
                row.get('Combined ATT&CK (Sub-)Technique ID')
                or row.get('ATT&CK Technique ID')
            )
            if tech and not pd.isna(tech):
                raw_entries.append((tech, passed_flag, rid))

    _accumulate_entries(raw_entries, aggregator)
    return _assemble_techniques(aggregator)


def build_layer(cis_data: dict, techniques: list[dict]) -> dict:
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


def convert_cis_to_attack(cis_data: dict) -> dict:
    """
    Load mapping, generate techniques, and build the full Navigator layer.
    """
    df = load_mapping(EX_MAP, SHEET_NAME)
    techniques = generate_techniques(cis_data, df)
    return build_layer(cis_data, techniques)


def combine_results(cis_data_list: list[dict]) -> dict:
    """
    Combine multiple CIS datasets at the rule level: if a rule fails in any,
    mark it as 'fail', otherwise 'pass'. Then run the normal CIS→ATT&CK
    conversion on the merged ruleset.
    """
    # merge all rules, failure wins
    merged: dict[str, dict] = {}
    for cis in cis_data_list:
        for rule in cis.get('rules', []):
            rid = rule.get('rule-id')
            if not rid:
                continue
            result = rule.get('result', '').lower()
            # initialize on first sight
            if rid not in merged:
                merged[rid] = {
                    'rule-id': rid,
                    'rule-title': rule.get('rule-title', ''),
                    # record lowercase so we can compare
                    'result': result
                }
            else:
                # once fail, always fail
                if result == 'fail':
                    merged[rid]['result'] = 'fail'

    # rebuild a combined cis_data dict
    combined_cis = {
        'benchmark-title': 'Combined CIS Benchmark',
        'rules': list(merged.values())
    }

    # return using the same functions
    return convert_cis_to_attack(combined_cis)
