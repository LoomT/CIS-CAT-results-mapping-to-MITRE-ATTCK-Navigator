import os
import pandas as pd

# Constants for mapping file
EX_MAP = 'CIS_Controls_v8_to_Enterprise_ATTCK_v82_Master_Mapping__5262021.xlsx'
SHEET_NAME = 'V8-ATT&CK Low (Sub-)Techniques'


def load_mapping(filename: str, sheet_name: str) -> pd.DataFrame:
    """
    Load the CIS-to-ATT&CK mapping Excel sheet, adding 'api/' prefix if needed.
    """
    if os.path.basename(os.getcwd()) != 'api':
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


def generate_techniques(cis_data: dict, df: pd.DataFrame) -> list[dict]:
    """
    Aggregate CIS rule results into ATT&CK techniques
    """

    # setup empty aggregator
    aggregator: dict[str, dict] = {}

    # iterate over items/rules in the input
    for rule in cis_data.get('rules', []):
        # parse rule name for mapping
        rid = rule.get('rule-id', '')
        parts = rid.split('_')
        if len(parts) < 4:
            continue

        result = rule.get('result', '').lower()
        raw = parts[3]
        segs = raw.split('.')
        high = segs[0]
        low = '.'.join(segs[:2])

        # match CIS control using the mapping
        matches = df[df['CIS Safeguard'].fillna('').str.startswith(low)]
        if matches.empty:
            matches = df[df['CIS Control'] == high]

        for _, row in matches.iterrows():
            tech = (row.get('Combined ATT&CK (Sub-)Technique ID')
                    or row.get('ATT&CK Technique ID'))
            if not tech or pd.isna(tech):
                continue

            entry = aggregator.setdefault(
                tech,
                {
                    'pass': 0,
                    'total': 0,
                    'comments': []
                }
            )
            # accumulate all rule results that apply to the technique
            entry['total'] += 1
            if result != 'fail':
                entry['pass'] += 1
            entry['comments'].append(rule.get('rule-title', ''))

    # format everything for the output
    techniques = []
    for tech_id, data in aggregator.items():
        total = data['total']
        passed = data['pass']
        frac = passed / total if total else 0
        techniques.append({
            'techniqueID': tech_id,
            'score': round(frac, 2),
            'color': gradient_color(frac),
            'comment': '\n'.join(data['comments'])
        })

    return techniques


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
