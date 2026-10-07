"""Seed trails and a few permits.

Usage:
    python seed.py            # seeds the local `trails` catalog directory
    python seed.py my_dir     # or another directory you passed to `pxt schema update`
"""
import sys
from pathlib import Path

import pixeltable as pxt

target = sys.argv[1] if len(sys.argv) > 1 else 'trails'
HERE = Path(__file__).resolve().parent

SEED = {
    'trails': [
        {'code': 'ENCH-01', 'name': 'Enchantment Lakes', 'region': 'cascades', 'miles': 18.5, 'difficulty': 'strenuous', 'open': True},
        {'code': 'HOH-02', 'name': 'Hoh River Trail', 'region': 'olympics', 'miles': 17.3, 'difficulty': 'moderate', 'open': True},
        {'code': 'MAPLE-03', 'name': 'Maple Pass Loop', 'region': 'cascades', 'miles': 7.2, 'difficulty': 'moderate', 'open': True},
        {'code': 'GLAC-04', 'name': 'Glacier Peak Meadows', 'region': 'cascades', 'miles': 24.0, 'difficulty': 'strenuous', 'open': False},
    ],
    'permits': [
        {'trail_code': 'ENCH-01', 'holder': 'R. Okoye', 'days': 3, 'party_size': 4, 'start_date': '2026-10-03', 'notes': None},
        {'trail_code': 'HOH-02', 'holder': 'M. Lindgren', 'days': 1, 'party_size': 2, 'start_date': '2026-10-04', 'notes': 'day hike'},
    ],
}

for table_name, rows in SEED.items():
    t = pxt.get_table(f'{target}/{table_name}')
    if t.count() > 0:
        print(f'{target}/{table_name} already has {t.count()} rows; skipping')
        continue
    for row in rows:
        for k, v in row.items():
            if isinstance(v, str) and v.startswith('data/'):
                row[k] = str(HERE / v)   # local sample media file
    t.insert(rows)
    print(f'inserted {len(rows)} rows into {target}/{table_name}')
