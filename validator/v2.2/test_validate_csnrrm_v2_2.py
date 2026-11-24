"""Run: python -m unittest -v test_validate_csnrrm_v2_2.py"""
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
import validate_csnrrm_v2_2 as V


def row(n, date='2025-01-01', time='08:00:00'):
    return dict(zip(V.FIELDS, [f'CSNRRM-OBS-{n:04d}', date, time, str(n),
                               'region', 'none', 'none', 'selected', 'high', 'public sample']))


def make_csv(folder, rows, columns=None):
    rows = [dict(r) for r in rows]
    for i, r in enumerate(rows):
        r['previous_observation_id'] = 'none' if i == 0 else rows[i-1]['observation_id']
        r['next_observation_id'] = 'none' if i == len(rows)-1 else rows[i+1]['observation_id']
    p = Path(folder) / 'sample.csv'
    with p.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns or V.FIELDS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    return p


class ValidatorV21Tests(unittest.TestCase):
    def check_issue(self, rows, issue, tamper=None, **kwargs):
        with tempfile.TemporaryDirectory() as d:
            p = make_csv(d, rows)
            if tamper:
                with p.open(encoding='utf-8', newline='') as f:
                    records = list(csv.DictReader(f))
                tamper(records)
                with p.open('w', encoding='utf-8', newline='') as f:
                    w = csv.DictWriter(f, fieldnames=V.FIELDS); w.writeheader(); w.writerows(records)
            result = V.validate(p, **kwargs)
            self.assertIn(issue, result['issue_counts'])

    def test_valid_and_hashes(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_csv(d, [row(1), row(2, '2025-01-02')])
            r = V.validate(p, expected_count=2)
            self.assertEqual(r['issues'], [])
            self.assertEqual(r['sha256'], hashlib.sha256(p.read_bytes()).hexdigest())
            self.assertEqual(r['validator_sha256'], hashlib.sha256(Path(V.__file__).read_bytes()).hexdigest())
            self.assertEqual(r['validation_parameters']['expected_count'], 2)
            self.assertEqual(r['counts']['confidence_high'], 2)

    def test_empty(self): self.check_issue([], 'empty_dataset')
    def test_count(self): self.check_issue([row(1)], 'unexpected_record_count', expected_count=2)
    def test_duplicate(self): self.check_issue([row(1), row(2)], 'duplicate_id', lambda r: r[1].update(observation_id=r[0]['observation_id']))
    def test_id_sequence(self): self.check_issue([row(1)], 'id_sequence', lambda r: r[0].update(observation_id='bad'))
    def test_sequence_order(self): self.check_issue([row(1)], 'sequence_order', lambda r: r[0].update(sequence_order='7'))
    def test_previous_link(self): self.check_issue([row(1),row(2)], 'previous_link', lambda r: r[1].update(previous_observation_id='bad'))
    def test_next_link(self): self.check_issue([row(1),row(2)], 'next_link', lambda r: r[0].update(next_observation_id='bad'))
    def test_missing_field(self): self.check_issue([row(1)], 'missing_or_extra_field', lambda r: r[0].update(source_type=''))
    def test_confidence(self): self.check_issue([row(1)], 'invalid_confidence_level', lambda r: r[0].update(confidence_level='unknown'))
    def test_region_whitespace(self): self.check_issue([row(1)], 'noncanonical_region_whitespace', lambda r: r[0].update(anatomical_region=' unknown'))

    def test_schema(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_csv(d, [row(1)], columns=V.FIELDS[:-1])
            self.assertIn('schema', V.validate(p)['issue_counts'])

    def test_invalid_encoding(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'sample.csv'; p.write_bytes(b'\xff\xfe')
            self.assertIn('invalid_encoding', V.validate(p)['issue_counts'])

    def test_bad_dates(self):
        for date, time in [('２０２５','unknown'),('٢٠٢٥','unknown'),('2025-02-30','unknown'),
                           ('2025-01-01','24:00:00'),('9999-12-31','unknown'),('2025','10:00:00')]:
            with self.subTest(date=date, time=time), self.assertRaises(ValueError):
                V.interval(date, time)

    def test_midnight_overlap_both_directions(self):
        for a, b in [('00:00:00','unknown'), ('unknown','00:00:00')]:
            with tempfile.TemporaryDirectory() as d:
                r = V.validate(make_csv(d,[row(1,time=a),row(2,time=b)]))
                self.assertEqual(r['counts']['temporally_ambiguous_adjacent_pairs'], 1)
                self.assertEqual(r['counts']['overlapping_all_record_pairs_including_ties'], 1)

    def test_ties(self):
        with tempfile.TemporaryDirectory() as d:
            r = V.validate(make_csv(d, [row(1),row(2),row(3)]))
            self.assertEqual(r['counts']['identical_timestamp_adjacent_pairs'], 2)
            self.assertEqual(r['counts']['identical_timestamp_all_record_pairs'], 3)
            self.assertEqual(r['counts']['overlapping_all_record_pairs_including_ties'], 3)

    def test_adjacent_inversion(self):
        self.check_issue([row(1,time='10:00:00'),row(2,time='09:00:00')], 'definite_chronological_inversion')

    def test_nonadjacent_inversion(self):
        self.check_issue([row(1,time='10:00:00'),row(2,time='unknown'),row(3,time='09:00:00')], 'nonadjacent_chronological_inversion')

    def test_nonadjacent_witness_when_adjacent_is_peak(self):
        self.check_issue([row(1,time='10:00:00'),row(2,time='11:00:00'),row(3,time='09:00:00')], 'nonadjacent_chronological_inversion')

    def test_max_date(self):
        self.check_issue([row(1,'2025-07-01')], 'date_after_max_date', max_date=datetime(2025,6,1))
        self.check_issue([row(1,'2025','unknown')], 'date_interval_exceeds_max_date', max_date=datetime(2025,6,1))

    def test_counts_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            r = row(1,'2025','unknown'); r['anatomical_region']='Unknown region'
            counts = V.validate(make_csv(d,[r]))['counts']
            self.assertEqual(counts['unknown_region'],1)
            self.assertEqual(counts['unknown_time'],1)
            self.assertEqual(counts['year_only_date'],1)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_csv(d,[row(1)])
            out = Path(d)/'result.json'
            cmd = [sys.executable, str(Path(V.__file__)), str(p), '--output', str(out), '--expected-count','1']
            proc = subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertEqual(json.loads(out.read_text())['validation_parameters']['expected_count'],1)
            proc = subprocess.run(cmd[:-1]+['2'],capture_output=True,text=True)
            self.assertEqual(proc.returncode,1)
            proc = subprocess.run([sys.executable,str(Path(V.__file__)),str(p),'--output',str(p)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,2)


if __name__ == '__main__':
    unittest.main()
