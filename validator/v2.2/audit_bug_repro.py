"""Reproduces platform-dependent bug (expected to FAIL on glibc/Linux). Run: python -m unittest -v audit_bug_repro"""
import unittest, validate_csnrrm_v2_2 as V
class YearBelow1000(unittest.TestCase):
    def test_documented_range_includes_0001_to_0999(self):
        for d in ('0001-01-01','0999-12-31'):
            with self.subTest(d=d): V.interval(d,'unknown')   # should not raise: documented range is 0001..9998
