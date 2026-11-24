"""NEW audit tests (not part of supplied files). Run: python -m unittest -v audit_new_tests"""
import unittest, tempfile, csv, re
from pathlib import Path
import validate_csnrrm_v2_2 as V
from test_v2_1_mutation_gaps import sample_row, validate_rows

class TieSite2(unittest.TestCase):
    def test_point_vs_containing_day_is_overlap_not_exact_tie(self):
        # point 00:00:00 vs same-day unknown time: overlap, starts equal, NOT an exact tie
        for a, b in [('00:00:00','unknown'), ('unknown','00:00:00'), ('12:00:00','unknown')]:
            r = validate_rows([sample_row(1,time=a), sample_row(2,time=b)])
            self.assertEqual(r['counts']['overlapping_all_record_pairs_including_ties'], 1)
            self.assertEqual(r['counts']['identical_timestamp_all_record_pairs'], 0)
            self.assertEqual(r['counts']['identical_timestamp_adjacent_pairs'], 0)
    def test_two_identical_imprecise_intervals_are_not_exact_ties(self):
        r = validate_rows([sample_row(1,time='unknown'), sample_row(2,time='unknown')])
        self.assertEqual(r['counts']['identical_timestamp_all_record_pairs'], 0)
        self.assertEqual(r['counts']['overlapping_all_record_pairs_including_ties'], 1)
    def test_nonadjacent_exact_tie_counted_globally_only(self):
        r = validate_rows([sample_row(1,time='10:00:00'), sample_row(2,'2025-01-02'), sample_row(3,time='10:00:00')])
        self.assertEqual(r['counts']['identical_timestamp_adjacent_pairs'], 0)
        self.assertEqual(r['counts']['identical_timestamp_all_record_pairs'], 1)

class YearBoundaryMessage(unittest.TestCase):
    def test_year_zero_and_9999_report_validator_message(self):
        for y in ('0000','9999'):
            with self.assertRaisesRegex(ValueError, r'year outside supported range'):
                V.interval(y,'unknown')
if __name__=='__main__': unittest.main()

# ---- Added: gap-closing tests for surviving auditor mutants ----
import subprocess, sys, json
from datetime import datetime
from test_validate_csnrrm_v2_2 import make_csv, row as trow

class GapClosers(unittest.TestCase):
    def _val(self, rows, **kw):
        with tempfile.TemporaryDirectory() as d:
            return V.validate(make_csv(d, rows), **kw)
    def test_bom_input_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_csv(d, [trow(1)]); p.write_bytes(b'\xef\xbb\xbf' + p.read_bytes())
            self.assertEqual(V.validate(p)['issues'], [])
    def test_whitespace_only_field_is_missing(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_csv(d, [trow(1)]); p.write_text(p.read_text().replace('public sample', '   '), encoding='utf-8')
            self.assertIn('missing_or_extra_field', V.validate(p)['issue_counts'])
    def test_lowercase_unknown_region_counted(self):
        r = trow(1); r['anatomical_region'] = 'unknown (limb, not confidently distinguishable)'
        self.assertEqual(self._val([r])['counts']['unknown_region'], 1)
    def test_invalid_timestamp_reported_through_validate(self):
        r = self._val([trow(1, '2025-02-30', 'unknown')])
        self.assertEqual(r['issue_counts'].get('invalid_timestamp'), 1)
    def test_oversize_field_reports_csv_parse_error(self):
        r = trow(1); r['source_type'] = 'a' * 200000
        self.assertIn('csv_parse_error', self._val([r])['issue_counts'])
    def test_day_interval_does_not_reach_next_midnight(self):
        for rows in ([trow(1,'2025-01-01','unknown'), trow(2,'2025-01-02','00:00:00')],
                     [trow(1,'2025','unknown'), trow(2,'2026-01-01','00:00:00')]):
            c = self._val(rows)['counts']
            self.assertEqual(c['overlapping_all_record_pairs_including_ties'], 0)
            self.assertEqual(c['temporally_ambiguous_adjacent_pairs'], 0)
    def test_max_date_boundaries(self):
        cut = datetime(2025,6,1)
        self.assertEqual(self._val([trow(1,'2025-06-01','unknown')], max_date=cut)['issues'], [])   # same-day imprecise: not straddling
        self.assertEqual(self._val([trow(1,'2025-06-01','23:59:59')], max_date=cut)['issues'], [])  # last second allowed
        self.assertEqual(self._val([trow(1,'2025-06-01','00:00:00')], max_date=cut)['issues'], [])  # start of cutoff day allowed
        self.assertIn('date_after_max_date', self._val([trow(1,'2025-06-02','00:00:00')], max_date=cut)['issue_counts'])
        self.assertIn('date_after_max_date', self._val([trow(1,'2025-06-02','unknown')], max_date=cut)['issue_counts'])
    def test_input_regex_strictness(self):
        for d,t in (('999','unknown'), ('2025-01-01','8:0:0'), ('2025-1-1','unknown')):
            with self.subTest(d=d,t=t), self.assertRaises(ValueError): V.interval(d,t)
    def test_cli_argument_guards(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_csv(d, [trow(1)]); out = Path(d)/'o.json'
            for extra in (['--expected-count','0'], ['--max-date','2025-02-30'], ['--max-date','2025-6-1']):
                pr = subprocess.run([sys.executable, V.__file__, str(p), '--output', str(out)] + extra, capture_output=True, text=True)
                self.assertEqual(pr.returncode, 2, extra)
