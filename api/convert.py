import pandas as pd
import json
import os

ex_map = 'CIS_Controls_v8_to_Enterprise_ATTCK_v82_Master_Mapping__5262021.xlsx'
if os.path.basename(os.getcwd()) != 'api':
    ex_map = 'api/' + ex_map


sheet_name = 'V8-ATT&CK Low (Sub-)Techniques'

# Load mapping sheet
df = pd.read_excel(ex_map, sheet_name=sheet_name, dtype=str)


def gradient_color(fraction):
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


def convert_cis_to_attack(input_path, output_path):
    cis_data = json.load(open(input_path))
    rules = cis_data.get('rules', [])

    aggregator = {}
    for rule in rules:
        rid = rule.get('rule-id', '')
        result = rule.get('result', '').lower()
        parts = rid.split('_')
        if len(parts) < 4:
            continue
        raw = parts[3]
        segs = raw.split('.')
        high = segs[0]
        low = ".".join(segs[:2])

        matches = df[df['CIS Safeguard'].fillna('').str.startswith(low)]
        if matches.empty:
            matches = df[df['CIS Control'] == high]

        for _, row in matches.iterrows():
            tech = row.get(
                'Combined ATT&CK (Sub-)Technique ID') \
                    or row.get('ATT&CK Technique ID')
            if not tech or pd.isna(tech):
                continue
            entry = aggregator.setdefault(
                tech, {'pass': 0, 'total': 0, 'comments': []})
            entry['total'] += 1
            if result != 'fail':
                entry['pass'] += 1
            entry['comments'].append(rule.get('rule-title', ''))

    # Build Navigator layer - output
    layer = {
        "version": "4.5.0",
        "name": cis_data.get('benchmark-title',
                             "MITRE ATT&CK NAVIGATOR LAYER"),
        "domain": "enterprise-attack",
        "description": "Aggregated CIS findings mapped to MITRE ATT&CK",
        "techniques": []
    }

    for tech, data in aggregator.items():
        total = data['total']
        passed = data['pass']
        frac = passed / total if total > 0 else 0
        color = gradient_color(frac)
        comments = "\n".join(data['comments'])
        layer['techniques'].append({
            "techniqueID": tech,
            "score": round(frac, 2),
            "color": color,
            "comment": comments
        })

    with open(output_path, 'w') as f:
        json.dump(layer, f, indent=2)

    print(
        f"Navigator layer written to {output_path} with \
            {len(layer['techniques'])} techniques.")
