#!/usr/bin/env python3
"""Create one isolated chronology-inversion probe for Comparison Demo v1.

Read-only source; writes a new CSV and a JSON manifest. Does not change
Validator v2.2 or the source data. This is an intentionally injected error,
not evidence that the source dataset contains an error.
"""
import csv
import hashlib
import io
import json
from datetime import datetime, timedelta
from pathlib import Path

SOURCE = Path('representative_observation_sample.csv')
OUTPUT = Path('chronology_probe_v1.csv')
MANIFEST = Path('chronology_probe_manifest_v1.json')


def bounds(date, time):
    if len(date) == 4:
        y = int(date)
        return datetime(y, 1, 1), datetime(y + 1, 1, 1) - timedelta(microseconds=1)
    day = datetime.strptime(date, '%Y-%m-%d')
    if time == 'unknown':
        return day, day + timedelta(days=1) - timedelta(microseconds=1)
    instant = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M:%S')
    return instant, instant


def main():
    if not SOURCE.is_file():
        raise SystemExit('Source CSV not found in current folder.')
    if OUTPUT.exists() or MANIFEST.exists():
        raise SystemExit('Output already exists; refusing to overwrite.')
    raw = SOURCE.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline=''))
    fields = reader.fieldnames
    rows = list(reader)
    if not fields or len(rows) < 2:
        raise SystemExit('Not enough valid CSV rows.')
    selected = None
    for i in range(len(rows)-1):
        a, b = rows[i], rows[i+1]
        try:
            start_a, end_a = bounds(a['observation_date'], a['observation_time'])
            start_b, end_b = bounds(b['observation_date'], b['observation_time'])
        except (ValueError, KeyError, OverflowError):
            continue
        if end_a < start_b:
            selected = i
            break
    if selected is None:
        raise SystemExit('No adjacent pair with definitely ordered nonoverlapping time intervals; no probe created.')
    i = selected
    before = []
    for j in (i, i+1):
        before.append({'row': j+2, 'id': rows[j]['observation_id'],
                       'date': rows[j]['observation_date'], 'time': rows[j]['observation_time']})
    for field in ('observation_date', 'observation_time'):
        rows[i][field], rows[i+1][field] = rows[i+1][field], rows[i][field]
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    output_bytes = buffer.getvalue().encode('utf-8')
    report = {
        'purpose': 'Controlled injected chronological inversion; not a source-data finding',
        'source_file': SOURCE.name, 'source_sha256': hashlib.sha256(raw).hexdigest(),
        'probe_file': OUTPUT.name, 'probe_sha256': hashlib.sha256(output_bytes).hexdigest(),
        'record_count': len(rows), 'modified_fields': ['observation_date', 'observation_time'],
        'modified_row_count': 2, 'before': before,
        'after': [{'row': j+2, 'id': rows[j]['observation_id'],
                   'date': rows[j]['observation_date'], 'time': rows[j]['observation_time']}
                  for j in (i, i+1)],
        'expected': 'A definite adjacent chronological inversion detectable by Validator v2.2; limited CONTROL does not compare row chronology',
    }
    OUTPUT.write_bytes(output_bytes)
    MANIFEST.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Created:', OUTPUT)
    print('Manifest:', MANIFEST)
    print('Records:', len(rows))
    print('Swapped date/time between:', before[0]['id'], 'and', before[1]['id'])
    print('Original source was not modified.')


if __name__ == '__main__':
    main()
