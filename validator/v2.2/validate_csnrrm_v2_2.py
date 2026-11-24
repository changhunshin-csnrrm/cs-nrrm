#!/usr/bin/env python3
"""CS-NRRM public representative CSV structural validator v2.2 (Python 3.9+).
Read-only input; structural checks do not verify original archive or clinical claims.
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
from datetime import datetime, timedelta
from pathlib import Path

VERSION = '2.2.0'
FIELDS = ['observation_id','observation_date','observation_time','sequence_order',
          'anatomical_region','previous_observation_id','next_observation_id',
          'source_type','confidence_level','observation_scope_note']
CONFIDENCE = {'high', 'medium', 'low'}


def interval(date, time):
    """Closed possible-time interval. Only ASCII YYYY, YYYY-MM-DD and HH:MM:SS."""
    if re.fullmatch(r'[0-9]{4}', date):
        year = int(date)
        if not 1 <= year <= 9998:
            raise ValueError('year outside supported range 0001..9998')
        if time != 'unknown':
            raise ValueError('year-only date requires unknown time')
        return datetime(year, 1, 1), datetime(year+1, 1, 1)-timedelta(microseconds=1)
    if not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', date):
        raise ValueError('date must be ASCII YYYY or YYYY-MM-DD')
    try:
        day = datetime.strptime(date, '%Y-%m-%d')
    except ValueError as exc:
        raise ValueError('invalid calendar date') from exc
    if f'{day.year:04d}-{day.month:02d}-{day.day:02d}' != date:
        raise ValueError('invalid canonical date')
    if day.year > 9998:
        raise ValueError('year outside supported range 0001..9998')
    if time == 'unknown':
        return day, day+timedelta(days=1)-timedelta(microseconds=1)
    if not re.fullmatch(r'[0-9]{2}:[0-9]{2}:[0-9]{2}', time):
        raise ValueError('time must be ASCII HH:MM:SS or unknown')
    try:
        clock = datetime.strptime(time, '%H:%M:%S').time()
    except ValueError as exc:
        raise ValueError('invalid clock time') from exc
    point = datetime.combine(day.date(), clock)
    return point, point


def validate(path, expected_count=None, max_date=None):
    path = Path(path)
    raw = path.read_bytes()
    issues = []
    try:
        decoded = raw.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        decoded = ''
        issues.append({'type': 'invalid_encoding', 'detail': 'Input must be UTF-8 or UTF-8 with BOM'})
    try:
        reader = csv.DictReader(io.StringIO(decoded, newline=''))
        columns = reader.fieldnames or []
        rows = list(reader)
    except (csv.Error, UnicodeError) as exc:
        columns, rows = [], []
        issues.append({'type': 'csv_parse_error', 'detail': str(exc)})
    if columns != FIELDS:
        issues.append({'type': 'schema', 'detail': 'Header must match expected ten columns in order'})
    if not rows:
        issues.append({'type': 'empty_dataset'})
    if expected_count is not None and len(rows) != expected_count:
        issues.append({'type': 'unexpected_record_count', 'expected': expected_count, 'actual': len(rows)})
    ids = [r.get('observation_id', '') or '' for r in rows]
    for identifier, frequency in sorted(Counter(ids).items()):
        if frequency > 1:
            issues.append({'type': 'duplicate_id', 'id': identifier})
    counts = Counter()
    intervals = []
    for i, row in enumerate(rows):
        rid = ids[i]
        if None in row or any(not isinstance(row.get(k), str) or not row.get(k, '').strip() for k in FIELDS):
            issues.append({'type': 'missing_or_extra_field', 'id': rid})
        if rid != f'CSNRRM-OBS-{i+1:04d}':
            issues.append({'type': 'id_sequence', 'id': rid, 'expected': f'CSNRRM-OBS-{i+1:04d}'})
        if row.get('sequence_order') != str(i+1):
            issues.append({'type': 'sequence_order', 'id': rid})
        expected_prev = 'none' if i == 0 else ids[i-1]
        expected_next = 'none' if i == len(rows)-1 else ids[i+1]
        if row.get('previous_observation_id') != expected_prev:
            issues.append({'type': 'previous_link', 'id': rid})
        if row.get('next_observation_id') != expected_next:
            issues.append({'type': 'next_link', 'id': rid})
        confidence = row.get('confidence_level', '') or ''
        if confidence not in CONFIDENCE:
            issues.append({'type': 'invalid_confidence_level', 'id': rid, 'value': confidence})
        else:
            counts['confidence_' + confidence] += 1
        if row.get('observation_time') == 'unknown':
            counts['unknown_time'] += 1
        region = row.get('anatomical_region') or ''
        if region.lower().startswith('unknown'):
            counts['unknown_region'] += 1
        if region != region.strip():
            issues.append({'type': 'noncanonical_region_whitespace', 'id': rid})
        if re.fullmatch(r'[0-9]{4}', row.get('observation_date') or ''):
            counts['year_only_date'] += 1
        try:
            bounds = interval(row.get('observation_date') or '', row.get('observation_time') or '')
            # An imprecise interval is after the cutoff only if its earliest possible time is later.
            # A separate issue reports intervals straddling the cutoff.
            if max_date is not None:
                cutoff_end = datetime.combine(max_date.date(), datetime.max.time())
                if bounds[0] > cutoff_end:
                    issues.append({'type': 'date_after_max_date', 'id': rid})
                elif bounds[1] > cutoff_end:
                    issues.append({'type': 'date_interval_exceeds_max_date', 'id': rid})
            intervals.append(bounds)
        except (ValueError, OverflowError) as exc:
            issues.append({'type': 'invalid_timestamp', 'id': rid, 'detail': str(exc)})
            intervals.append(None)
    ambiguous_adjacent, tied_adjacent = [], []
    for i in range(1, len(rows)):
        a, b = intervals[i-1], intervals[i]
        if a is None or b is None:
            continue
        pair = {'previous_id': ids[i-1], 'current_id': ids[i]}
        if a[0] > b[1]:
            issues.append({'type': 'definite_chronological_inversion', **pair})
        elif a[0] == a[1] == b[0] == b[1]:
            tied_adjacent.append(pair)
        elif a[0] <= b[1] and b[0] <= a[1]:
            ambiguous_adjacent.append(pair)
    # At most one witness per later row, excluding the adjacent pair (already checked).
    # Track max start among indices <= i-2; do not suppress a valid nonadjacent witness.
    latest_start, latest_index = None, None
    for i, bounds in enumerate(intervals):
        if i >= 2:
            candidate = intervals[i-2]
            if candidate is not None and (latest_start is None or candidate[0] > latest_start):
                latest_start, latest_index = candidate[0], i-2
        if bounds is not None and latest_start is not None and latest_start > bounds[1]:
            issues.append({'type': 'nonadjacent_chronological_inversion',
                           'earlier_id': ids[latest_index], 'later_id': ids[i]})
    global_overlap_count = 0
    exact_tie_pairs = 0
    for i, a in enumerate(intervals):
        if a is None:
            continue
        for b in intervals[i+1:]:
            if b is not None and a[0] <= b[1] and b[0] <= a[1]:
                global_overlap_count += 1
                if a[0] == a[1] == b[0] == b[1]:
                    exact_tie_pairs += 1
    counts['temporally_ambiguous_adjacent_pairs'] = len(ambiguous_adjacent)
    counts['identical_timestamp_adjacent_pairs'] = len(tied_adjacent)
    counts['overlapping_all_record_pairs_including_ties'] = global_overlap_count
    counts['identical_timestamp_all_record_pairs'] = exact_tie_pairs
    issue_counts = Counter(issue['type'] for issue in issues)
    return {
        'validator_version': VERSION,
        'source_file': path.name,
        'sha256': hashlib.sha256(raw).hexdigest(),
        'validator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'runtime': {'python': platform.python_version(), 'platform': platform.platform()},
        'validation_parameters': {'expected_count': expected_count,
                                 'max_date': f'{max_date.year:04d}-{max_date.month:02d}-{max_date.day:02d}' if max_date else None},
        'record_count': len(rows), 'columns': columns,
        'counts': dict(sorted(counts.items())),
        'temporally_ambiguous_adjacent_pairs': ambiguous_adjacent,
        'identical_timestamp_adjacent_pairs': tied_adjacent,
        'issue_counts': dict(sorted(issue_counts.items())), 'issues': issues,
        'interpretation': ('Structural checks on this public CSV only. Row-derived IDs and links do not prove '
                           'continuity in the private archive. Interval overlap is not an ordering error. '
                           'No private-original, clinical, or ground-truth verification.')
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_file', type=Path)
    parser.add_argument('--output', type=Path, default=Path('validation_result_v2_2.json'))
    parser.add_argument('--expected-count', type=int, default=None)
    parser.add_argument('--max-date', type=str, default=None, help='Optional cutoff YYYY-MM-DD')
    args = parser.parse_args()
    if not args.csv_file.is_file():
        parser.error('CSV file not found')
    max_date = None
    if args.max_date:
        try:
            max_date = datetime.strptime(args.max_date, '%Y-%m-%d')
            if f'{max_date.year:04d}-{max_date.month:02d}-{max_date.day:02d}' != args.max_date:
                raise ValueError('noncanonical date')
        except ValueError:
            parser.error('--max-date must be a valid YYYY-MM-DD')
    if args.expected_count is not None and args.expected_count < 1:
        parser.error('--expected-count must be >= 1')
    if args.output.resolve() == args.csv_file.resolve():
        parser.error('--output cannot overwrite input CSV')
    result = validate(args.csv_file, args.expected_count, max_date)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('record_count', 'counts', 'issue_counts')}, indent=2))
    print('Saved:', args.output)
    sys.exit(1 if result['issues'] else 0)


if __name__ == '__main__':
    main()
