import subprocess, tempfile, sys, shutil
from pathlib import Path
SRC=Path('/home/claude/cs-nrrm/validator/v2.2'); v=SRC/'validate_csnrrm_v2_2.py'
src=v.read_text(encoding='utf-8')
files=['test_validate_csnrrm_v2_2.py','test_v2_1_mutation_gaps.py','audit_new_tests.py','audit_bug_repro.py']
extra=sys.argv[1:]  # optional extra test modules from /tmp/rev
M=[
('X01 adjacent None-skip continue->pass', "        if a is None or b is None:\n            continue\n        pair", "        if a is None or b is None:\n            pass\n        pair"),
('X02 nonadj candidate None guard removed', 'if candidate is not None and (latest_start', 'if (latest_start'),
('X03 nonadj bounds None guard removed', 'if bounds is not None and latest_start is not None and', 'if latest_start is not None and'),
('X04 global a None skip removed', "        if a is None:\n            continue\n        for b in", "        for b in"),
('X05 global b None guard removed', 'if b is not None and a[0] <= b[1]', 'if a[0] <= b[1]'),
('X06 global overlap drops a[0]<=b[1] clause', 'if b is not None and a[0] <= b[1] and b[0] <= a[1]:', 'if b is not None and b[0] <= a[1]:'),
('X07 global tie requires only a[0]==b[0] in tie-count', "if a[0] == a[1] == b[0] == b[1]:\n                    exact_tie_pairs", "if a[0] == b[0]:\n                    exact_tie_pairs"),
('X08 short-row isinstance guard removed', "any(not isinstance(row.get(k), str) or not row.get(k, '').strip() for k in FIELDS)", "any(not (row.get(k) or '').strip() for k in FIELDS)"),
('X09 extra-field detection (None in row) removed', 'if None in row or any(', 'if any('),
('X10 year-only count regex ASCII->\\d', "re.fullmatch(r'[0-9]{4}', row.get('observation_date') or '')", "re.fullmatch(r'\\d{4}', row.get('observation_date') or '')"),
('X11 year-only interval regex fullmatch->match', "if re.fullmatch(r'[0-9]{4}', date):", "if re.match(r'[0-9]{4}', date):"),
('X12 time regex ASCII->\\d', "re.fullmatch(r'[0-9]{2}:[0-9]{2}:[0-9]{2}', time)", "re.fullmatch(r'\\d{2}:\\d{2}:\\d{2}', time)"),
('X13 date regex ASCII->\\d (canonical check backstops)', "re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', date)", "re.fullmatch(r'\\d{4}-\\d{2}-\\d{2}', date)"),
('X14 day end -1us -> -1s (equiv at 1s granularity?)', "return day, day+timedelta(days=1)-timedelta(microseconds=1)", "return day, day+timedelta(days=1)-timedelta(seconds=1)"),
('X15 year-only end -1us -> -1s', "datetime(year+1, 1, 1)-timedelta(microseconds=1)", "datetime(year+1, 1, 1)-timedelta(seconds=1)"),
('X16 report record_count -> 0', "'record_count': len(rows)", "'record_count': 0"),
('X17 report ambiguous pair list -> []', "'temporally_ambiguous_adjacent_pairs': ambiguous_adjacent,", "'temporally_ambiguous_adjacent_pairs': [],"),
('X18 report max_date param -> None', "'max_date': f'{max_date.year:04d}-{max_date.month:02d}-{max_date.day:02d}' if max_date else None", "'max_date': None"),
('X19 report columns -> []', "'columns': columns,", "'columns': [],"),
('X20 except drops OverflowError (reachable?)', "except (ValueError, OverflowError) as exc:", "except ValueError as exc:"),
('X21 remove canonical-date backstop', "    if f'{day.year:04d}-{day.month:02d}-{day.day:02d}' != date:\n        raise ValueError('invalid canonical date')\n", ""),
('X22 cutoff end-of-day -> start-of-day', 'datetime.max.time()', 'datetime.min.time()'),
('X23 interval invalid_timestamp detail dropped', "'detail': str(exc)})\n            intervals.append(None)", "})\n            intervals.append(None)"),
('X24 unknown_region startswith -> ==', "region.lower().startswith('unknown')", "region.lower() == 'unknown'"),
('X25 exit code always 0', "sys.exit(1 if result['issues'] else 0)", "sys.exit(0)"),
('X26 adjacent loop range start 1->2', 'for i in range(1, len(rows)):\n        a, b', 'for i in range(2, len(rows)):\n        a, b'),
('X27 nonadj threshold i>=2 -> i>=3', 'if i >= 2:', 'if i >= 3:'),
('X28 nonadj uses intervals[i-1]', 'candidate = intervals[i-2]', 'candidate = intervals[i-1]'),
('X29 duplicate-id report id dropped', "issues.append({'type': 'duplicate_id', 'id': identifier})", "issues.append({'type': 'duplicate_id'})"),
('X30 sequence_order compare str(i+1)->str(i)', "!= str(i+1)", "!= str(i)"),
('X31 invalid_confidence value field dropped', ", 'value': confidence})", "})"),
('X32 year-only requires unknown time: raise->pass', "raise ValueError('year-only date requires unknown time')", "pass"),
]
extra_mods=[Path(e).stem for e in extra]
surv=0;kill=0;skip=0
for name,old,new in M:
    c=src.count(old)
    if c!=1: print('SKIP(%d)'%c,name); skip+=1; continue
    with tempfile.TemporaryDirectory() as d:
        Path(d,v.name).write_text(src.replace(old,new),encoding='utf-8')
        for f in files: shutil.copy2(SRC/f,d)
        for e in extra: shutil.copy2(e,d)
        r=subprocess.run([sys.executable,'-m','unittest']+[Path(f).stem for f in files]+extra_mods,cwd=d,capture_output=True,text=True,timeout=120)
    if r.returncode: kill+=1; print('KILLED  ',name)
    else: surv+=1; print('SURVIVED',name)
print(f'my mutants: killed={kill} survived={surv} skipped={skip}')
