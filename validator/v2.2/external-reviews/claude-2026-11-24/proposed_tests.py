"""Proposed additional tests (reviewer-authored). Run: python -m unittest -v proposed_tests"""
import csv, json, tempfile, unittest
from pathlib import Path
import validate_csnrrm_v2_2 as V
from test_validate_csnrrm_v2_2 import make_csv, row

def val(rows, **kw):
    with tempfile.TemporaryDirectory() as d:
        return V.validate(make_csv(d, rows), **kw)

def val_raw(text, **kw):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d)/'r.csv'; p.write_text(text, encoding='utf-8', newline=''); return V.validate(p, **kw)

class InvalidTimestampNeighbours(unittest.TestCase):
    def test_invalid_row_between_valid_rows_does_not_crash_and_is_isolated(self):
        r = val([row(1,'2025-01-01','08:00:00'), row(2,'2025-02-30','unknown'), row(3,'2025-01-02','08:00:00')])
        self.assertEqual(r['issue_counts'], {'invalid_timestamp': 1})
        self.assertEqual(r['counts']['overlapping_all_record_pairs_including_ties'], 0)
    def test_invalid_first_and_last_rows(self):
        r = val([row(1,'bad','unknown'), row(2), row(3,'bad','unknown')])
        self.assertEqual(r['issue_counts'], {'invalid_timestamp': 2})
    def test_all_rows_invalid(self):
        r = val([row(1,'x','unknown'), row(2,'y','unknown')])
        self.assertEqual(r['issue_counts'], {'invalid_timestamp': 2})
    def test_inversion_across_invalid_row_still_reported(self):
        r = val([row(1,time='10:00:00'), row(2,'bad','unknown'), row(3,time='09:00:00')])
        self.assertEqual(r['issue_counts'].get('nonadjacent_chronological_inversion'), 1)

class OverlapCountSemantics(unittest.TestCase):
    def test_definite_inversion_is_not_counted_as_overlap(self):
        r = val([row(1,time='10:00:00'), row(2,time='09:00:00')])
        self.assertEqual(r['counts']['overlapping_all_record_pairs_including_ties'], 0)
        self.assertEqual(r['counts']['temporally_ambiguous_adjacent_pairs'], 0)
    def test_nonadjacent_inversion_not_counted_as_overlap(self):
        r = val([row(1,time='10:00:00'), row(2,'2025-01-05','unknown'), row(3,time='09:00:00')])
        self.assertEqual(r['counts']['overlapping_all_record_pairs_including_ties'], 0)

class RowShape(unittest.TestCase):
    def test_short_row(self):
        hdr = ','.join(V.FIELDS)
        r = val_raw(hdr + '\r\nCSNRRM-OBS-0001,2025-01-01,08:00:00,1\r\n')
        self.assertIn('missing_or_extra_field', r['issue_counts'])
    def test_extra_field(self):
        hdr = ','.join(V.FIELDS)
        good = ['CSNRRM-OBS-0001','2025-01-01','08:00:00','1','r','none','none','s','high','n']
        r = val_raw(hdr + '\r\n' + ','.join(good) + ',EXTRA\r\n')
        self.assertIn('missing_or_extra_field', r['issue_counts'])

class UnicodeAndWhitespace(unittest.TestCase):
    def test_non_ascii_digit_time_rejected(self):
        for t in ('٠٨:٠٠:٠٠', '０８:００:００'):
            with self.subTest(t=t), self.assertRaises(ValueError): V.interval('2025-01-01', t)
    def test_non_ascii_digit_date_rejected_in_validate(self):
        r = val([row(1,'٢٠٢٥-٠١-٠١','unknown')])
        self.assertEqual(r['issue_counts'].get('invalid_timestamp'), 1)
    def test_year_only_count_ignores_non_ascii_digit_year(self):
        r = val([row(1,'２０２５','unknown')])
        self.assertEqual(r['counts'].get('year_only_date',0), 0)

class ReportContent(unittest.TestCase):
    def test_report_fields(self):
        from datetime import datetime
        with tempfile.TemporaryDirectory() as d:
            p = make_csv(d, [row(1,time='unknown'), row(2,time='10:00:00')])
            r = V.validate(p, expected_count=2, max_date=datetime(2025,6,1))
        self.assertEqual(r['record_count'], 2)
        self.assertEqual(r['columns'], V.FIELDS)
        self.assertEqual(r['validation_parameters'], {'expected_count': 2, 'max_date': '2025-06-01'})
        self.assertEqual(r['temporally_ambiguous_adjacent_pairs'],
                         [{'previous_id':'CSNRRM-OBS-0001','current_id':'CSNRRM-OBS-0002'}])
        json.dumps(r)
    def test_issue_payloads(self):
        r = val([row(1), row(2)])  # baseline clean
        self.assertEqual(r['issues'], [])
        r = val([row(1), dict(row(2), confidence_level='bogus')])
        self.assertIn({'type':'invalid_confidence_level','id':'CSNRRM-OBS-0002','value':'bogus'}, r['issues'])
        r = val([row(1,'2025-02-30','unknown')])
        self.assertEqual(r['issues'][0]['type'], 'invalid_timestamp'); self.assertTrue(r['issues'][0]['detail'])
    def test_duplicate_id_payload(self):
        with tempfile.TemporaryDirectory() as d:
            p = make_csv(d, [row(1), row(2)])
            recs = list(csv.DictReader(p.open(encoding='utf-8', newline='')))
            recs[1]['observation_id'] = recs[0]['observation_id']
            with p.open('w', encoding='utf-8', newline='') as f:
                w = csv.DictWriter(f, fieldnames=V.FIELDS); w.writeheader(); w.writerows(recs)
            r = V.validate(p)
        self.assertIn({'type':'duplicate_id','id':'CSNRRM-OBS-0001'}, r['issues'])
if __name__ == '__main__': unittest.main()

class MoreNoneAndDigitCases(unittest.TestCase):
    def test_invalid_row_after_two_valid_rows(self):      # kills "bounds is not None" guard removal
        r = val([row(1), row(2,'2025-01-02'), row(3,'bad','unknown')])
        self.assertEqual(r['issue_counts'], {'invalid_timestamp': 1})
    def test_mixed_ascii_and_non_ascii_digit_time_rejected(self):
        with self.assertRaises(ValueError): V.interval('2025-01-01', '1\u0668:00:00')   # '1' + ARABIC-INDIC EIGHT
