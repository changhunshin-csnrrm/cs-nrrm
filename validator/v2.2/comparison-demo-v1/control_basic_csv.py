#!/usr/bin/env python3
"""Comparison Demo v1.0: deliberately limited basic CSV CONTROL.

Checks CSV readability, exact columns, nonempty cells, unique observation IDs,
canonical date/time syntax, and confidence vocabulary. Does NOT check record
order, cross-row links, chronology, interval overlaps, or provenance truth.
Read-only input. No clinical or independent validation claims.
"""
import argparse
import csv
import hashlib
import io
import json
import platform
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

FIELDS = ['observation_id', 'observation_date', 'observation_time', 'sequence_order',
          'anatomical_region', 'previous_observation_id', 'next_observation_id',
          'source_type', 'confidence_level', 'observation_scope_note']
CONFIDENCE = {'high', 'medium', 'low'}


def valid_timestamp(date, time):
    """Same basic timestamp acceptance as v2.2; no ordering comparisons."""
    if re.fullmatch(r'[0-9]{4}', date):
        return 1 <= int(date) <= 9998 and time == 'unknown'
    if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', date):
        return False
    try:
        day = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return False
    if day.year > 9998 or f'{day.year:04d}-{day.month:02d}-{day.day:02d}' != date:
        return False
    if time == 'unknown':
        return True
    if not re.fullmatch(r'[0-9]{2}:[0-9]{2}:[0-9]{2}', time):
        return False
    try:
        datetime.strptime(time, '%H:%M:%S')
        return True
    except ValueError:
        return False


def validate(path):
    raw = path.read_bytes()
    issues = []
    try:
        decoded = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        decoded = ''
        issues.append({'type': 'invalid_encoding'})
    try:
        reader = csv.DictReader(io.StringIO(decoded, newline=''))
        columns = reader.fieldnames or []
        rows = list(reader)
    except (csv.Error, UnicodeError) as exc:
        columns, rows = [], []
        issues.append({'type': 'csv_parse_error', 'detail': str(exc)})
    if columns != FIELDS:
        issues.append({'type': 'schema', 'detail': 'Expected ten columns in fixed order'})
    if not rows:
        issues.append({'type': 'empty_dataset'})
    ids = [r.get('observation_id') or '' for r in rows]
    for identifier, count in sorted(Counter(ids).items()):
        if count > 1:
            issues.append({'type': 'duplicate_id', 'id': identifier})
    for row in rows:
        rid = row.get('observation_id') or ''
        if None in row or any(not isinstance(row.get(k), str) or not row.get(k, '').strip() for k in FIELDS):
            issues.append({'type': 'missing_or_extra_field', 'id': rid})
        if not valid_timestamp(row.get('observation_date') or '', row.get('observation_time') or ''):
            issues.append({'type': 'invalid_timestamp', 'id': rid})
        if (row.get('confidence_level') or '') not in CONFIDENCE:
            issues.append({'type': 'invalid_confidence_level', 'id': rid})
    return {
        'control_version': '1.0.0',
        'scope': 'Limited basic CSV CONTROL; not a representative baseline for all ETL systems',
        'source_file': path.name,
        'sha256': hashlib.sha256(raw).hexdigest(),
        'control_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'runtime': {'python': platform.python_version(), 'platform': platform.platform()},
        'record_count': len(rows),
        'columns': columns,
        'issue_counts': dict(sorted(Counter(i['type'] for i in issues).items())),
        'issues': issues,
        'not_tested': ['record ID sequence', 'sequence_order chronology',
                       'previous/next record links', 'chronological inversions',
                       'time interval overlap', 'actual source provenance'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_file', type=Path)
    parser.add_argument('--output', type=Path, default=Path('control_result_v1.json'))
    args = parser.parse_args()
    if not args.csv_file.is_file():
        parser.error('CSV file not found')
    if args.output.resolve() == args.csv_file.resolve():
        parser.error('--output cannot overwrite input CSV')
    result = validate(args.csv_file)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('record_count', 'issue_counts')}, indent=2))
    print('Saved:', args.output)
    sys.exit(1 if result['issues'] else 0)


if __name__ == '__main__':
    main()
