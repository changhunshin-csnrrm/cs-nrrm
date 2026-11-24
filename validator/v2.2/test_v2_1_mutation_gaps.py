"""Additional mutation-gap tests for CS-NRRM Validator v2.1.
Run: python -m unittest -v test_v2_1_mutation_gaps.py
Does not modify the validator or the public CSV.
"""
import tempfile
import unittest
from pathlib import Path

import validate_csnrrm_v2_2 as V


def sample_row(n, date='2025-01-01', time='08:00:00'):
    return dict(zip(V.FIELDS, [f'CSNRRM-OBS-{n:04d}', date, time, str(n),
                               'region', 'none', 'none', 'selected', 'high', 'public sample']))


def validate_rows(rows):
    import csv
    for i, r in enumerate(rows):
        r['previous_observation_id'] = 'none' if i == 0 else rows[i-1]['observation_id']
        r['next_observation_id'] = 'none' if i == len(rows)-1 else rows[i+1]['observation_id']
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'test.csv'
        with path.open('w', encoding='utf-8', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=V.FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        return V.validate(path)


class MutationGapTests(unittest.TestCase):
    def test_nonadjacent_equal_boundary_is_not_inversion(self):
        result = validate_rows([
            sample_row(1, time='10:00:00'),
            sample_row(2, time='unknown'),
            sample_row(3, time='10:00:00'),
        ])
        self.assertNotIn('nonadjacent_chronological_inversion', result['issue_counts'])

    def test_equal_latest_start_keeps_first_witness(self):
        result = validate_rows([
            sample_row(1, time='10:00:00'),
            sample_row(2, time='10:00:00'),
            sample_row(3, time='unknown'),
            sample_row(4, time='09:00:00'),
        ])
        witnesses = [i for i in result['issues'] if i['type'] == 'nonadjacent_chronological_inversion'
                     and i['later_id'] == 'CSNRRM-OBS-0004']
        self.assertEqual(len(witnesses), 1)
        self.assertEqual(witnesses[0]['earlier_id'], 'CSNRRM-OBS-0001')

    def test_unsupported_year_boundaries(self):
        for year in ('0000', '9999'):
            with self.subTest(year=year):
                with self.assertRaises(ValueError):
                    V.interval(year, 'unknown')


if __name__ == '__main__':
    unittest.main()
