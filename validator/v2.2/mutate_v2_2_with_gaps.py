"""Mutation testing for CS-NRRM Validator v2.2. Run beside validator and tests.
Only temporary copies are modified. Mutation score is specific to these mutants.
"""
import subprocess, tempfile, sys, shutil
from pathlib import Path

SOURCE = Path(__file__).resolve().parent
validator = SOURCE / 'validate_csnrrm_v2_2.py'
tests = SOURCE / 'test_validate_csnrrm_v2_2.py'
gap_tests = SOURCE / 'test_v2_1_mutation_gaps.py'
audit_tests = SOURCE / 'audit_new_tests.py'
bug_tests = SOURCE / 'audit_bug_repro.py'
if not all(p.is_file() for p in (validator, tests, gap_tests, audit_tests, bug_tests)):
    sys.exit('Place this script beside validate_csnrrm_v2_2.py and test_validate_csnrrm_v2_2.py')
src = validator.read_text(encoding='utf-8')
M = [
 ('adjacent inversion > to >=', 'if a[0] > b[1]:', 'if a[0] >= b[1]:'),
 ('adjacent overlap inclusive to strict', 'elif a[0] <= b[1] and b[0] <= a[1]:', 'elif a[0] < b[1] and b[0] < a[1]:'),
 ('nonadjacent > to >=', 'latest_start > bounds[1]:', 'latest_start >= bounds[1]:'),
 ('nonadjacent candidate > to >=', 'candidate[0] > latest_start', 'candidate[0] >= latest_start'),
 ('global overlap inclusive to strict', 'if b is not None and a[0] <= b[1] and b[0] <= a[1]:', 'if b is not None and a[0] < b[1] and b[0] < a[1]:'),
 ('drop previous_link check', "if row.get('previous_observation_id') != expected_prev:", 'if False:'),
 ('drop next_link check', "if row.get('next_observation_id') != expected_next:", 'if False:'),
 ('drop sequence_order check', "if row.get('sequence_order') != str(i+1):", 'if False:'),
 ('drop id_sequence check', "if rid != f'CSNRRM-OBS-{i+1:04d}':", 'if False:'),
 ('drop duplicate_id check', 'if frequency > 1:', 'if False:'),
 ('drop schema check', 'if columns != FIELDS:', 'if False:'),
 ('drop max_date after check', 'if bounds[0] > cutoff_end:', 'if False:'),
 ('drop max_date interval straddle', 'elif bounds[1] > cutoff_end:', 'elif False:'),
 ('drop missing_or_extra_field', 'if None in row or any(', 'if False and any('),
 ('confidence set add unknown', "CONFIDENCE = {'high', 'medium', 'low'}", "CONFIDENCE = {'high', 'medium', 'low', 'unknown'}"),
 ('year range 1..9998 to 0..9999', 'if not 1 <= year <= 9998:', 'if not 0 <= year <= 9999:'),
 ('year-only requires unknown drop', "if time != 'unknown':\n            raise ValueError('year-only date requires unknown time')", "if False:\n            raise ValueError('x')"),
 ('unknown_region case insensitive to sensitive', "region.lower().startswith('unknown')", "region.startswith('unknown')"),
 ('tie both sites to starts equal', 'a[0] == a[1] == b[0] == b[1]', 'a[0] == b[0]'),
 ('drop empty_dataset', 'if not rows:', 'if False:'),
 ('drop expected_count', 'if expected_count is not None and len(rows) != expected_count:', 'if False:'),
 ('drop confidence tally', "counts['confidence_' + confidence] += 1", 'pass'),
 ('drop year_only tally', "counts['year_only_date'] += 1", 'pass'),
 ('drop unknown_time tally', "counts['unknown_time'] += 1", 'pass'),
 ('replace csv sha256', 'hashlib.sha256(raw).hexdigest()', "'0'"),
 ('replace validator sha256', 'hashlib.sha256(Path(__file__).read_bytes()).hexdigest()', "'0'"),
 ('drop ambiguous append', 'ambiguous_adjacent.append(pair)', 'pass'),
 ('drop exact ties count', 'exact_tie_pairs += 1', 'pass'),
 ('drop whitespace region check', 'if region != region.strip():', 'if False:'),
 ('drop invalid encoding issue', "issues.append({'type': 'invalid_encoding', 'detail': 'Input must be UTF-8 or UTF-8 with BOM'})", 'pass'),
]
with tempfile.TemporaryDirectory() as d:
    shutil.copy2(validator, Path(d) / validator.name)
    shutil.copy2(tests, Path(d) / tests.name)
    shutil.copy2(gap_tests, Path(d) / gap_tests.name)
    shutil.copy2(audit_tests, Path(d) / audit_tests.name)
    shutil.copy2(bug_tests, Path(d) / bug_tests.name)
    baseline = subprocess.run([sys.executable, '-m', 'unittest', tests.stem, gap_tests.stem, audit_tests.stem, bug_tests.stem], cwd=d, capture_output=True, text=True, timeout=30)
    if baseline.returncode:
        sys.exit('BASELINE TESTS FAILED:\n' + baseline.stdout + baseline.stderr)
print('Baseline: PASS')
killed = survived = skipped = 0
for name, old, new in M:
    matches = src.count(old)
    if matches != (2 if name == 'tie both sites to starts equal' else 1):
        skipped += 1
        print(f'SKIP ({matches} matches): {name}')
        continue
    with tempfile.TemporaryDirectory() as d:
        Path(d, validator.name).write_text(src.replace(old, new), encoding='utf-8')
        shutil.copy2(tests, Path(d) / tests.name)
        shutil.copy2(gap_tests, Path(d) / gap_tests.name)
        shutil.copy2(audit_tests, Path(d) / audit_tests.name)
        shutil.copy2(bug_tests, Path(d) / bug_tests.name)
        result = subprocess.run([sys.executable, '-m', 'unittest', tests.stem, gap_tests.stem, audit_tests.stem, bug_tests.stem], cwd=d, capture_output=True, text=True, timeout=30)
    if result.returncode:
        killed += 1
        print('KILLED  ', name)
    else:
        survived += 1
        print('SURVIVED', name)
total = killed + survived
print(f'\nmutants={total} killed={killed} survived={survived} skipped={skipped} score={killed/total:.0%}' if total else 'No applicable mutations')
