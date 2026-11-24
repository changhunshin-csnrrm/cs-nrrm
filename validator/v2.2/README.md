# CS-NRRM™ Validator v2.2

**Structural Validation for Longitudinal Observation Records**

Version: 2.2.0  
Release preparation date: November 24, 2026  
Developer: Changhun Shin  
Framework: CS-NRRM™ (Changhun Shin Natural Recovery Pattern Model)

## Overview

CS-NRRM™ Validator v2.2 is a Python-based structural validation tool for longitudinal observation records.

It is designed to check whether records preserve structural consistency across time, including chronology, continuity, observation identifiers, record relationships, temporal ambiguity, and selected provenance-related metadata.

The validator is non-medical and non-clinical. It does not diagnose conditions, recommend treatments, determine recovery effectiveness, or predict future health outcomes.

## Key Capabilities

- Validate CSV schema and required fields.
- Check observation identifiers and sequence order.
- Verify previous and next observation links.
- Detect chronological inversions and overlapping temporal intervals.
- Record temporal ambiguity and identical timestamps.
- Apply date-boundary validation rules.
- Report confidence and unknown-value counts.
- Generate structured JSON validation results.
- Calculate SHA-256 file-integrity references.

## Requirements

- Python 3.13 (tested with Python 3.13.17 on Windows).
- Python standard library.
- No additional Python packages required for the documented test commands.

## Files

| File | Purpose |
|---|---|
| `validate_csnrrm_v2_2.py` | Validator implementation |
| `test_validate_csnrrm_v2_2.py` | Main automated tests |
| `test_v2_1_mutation_gaps.py` | Additional mutation-gap tests |
| `audit_new_tests.py` | Additional audit regression tests |
| `audit_bug_repro.py` | Date-boundary regression test |
| `mutate_v2_2_with_gaps.py` | Mutation testing script |
| `representative_observation_sample.csv` | Public representative dataset |
| `validation_result_v2_2.json` | Representative validation output |
| `Final_Technical_Audit_v2.2.md` | Technical validation report |

## Quick Start

Open a terminal in the directory containing the files.

### 1. Run the automated tests

```bash
python -m unittest -v test_validate_csnrrm_v2_2 test_v2_1_mutation_gaps audit_new_tests audit_bug_repro
```

**Reported result:** 39 tests passed.

### 2. Run mutation testing

```bash
python mutate_v2_2_with_gaps.py
```

**Observed result:**

```text
Baseline: PASS
mutants=30 killed=30 survived=0 skipped=0 score=100%
```

All 30 predefined, executed mutations were detected by the test suite.

The mutation score does not establish exhaustive software correctness.

### 3. Validate the representative dataset

```bash
python validate_csnrrm_v2_2.py representative_observation_sample.csv --expected-count 585 --output validation_result_v2_2.json
```

**Reported results:**

- Total records: 585
- Structural validation issues: 0
- High-confidence records: 503
- Medium-confidence records: 48
- Low-confidence records: 34
- Temporally ambiguous adjacent pairs: 34
- All-record overlapping pairs, including ties: 432

These are structural validation results, not clinical findings.

## File Integrity

SHA-256 of `validate_csnrrm_v2_2.py`:

```text
d5f79ffbbfc648e1c1b8f3e8eda95b88290e68600edc7ccf1604eb71364b2e5d
```

SHA-256 of `representative_observation_sample.csv`:

```text
745beb502ee5ed4641ce1b4226315b45973effec304ba965e9513ad7292dfa13
```

Both reference values were confirmed using Windows `certutil` on November 24, 2026.

## Validation Status

| Validation | Reported Result |
|---|---|
| Automated tests | 39 passed |
| Mutation testing | 30/30 killed |
| Surviving mutants | 0 |
| Skipped mutants | 0 |
| Mutation score | 100% |
| Representative CSV | 585 records, 0 reported issues |
| Independent third-party certification | Not obtained |

These results document developer-executed technical testing within a defined scope.

External researchers are encouraged to independently inspect the source code, reproduce the tests, and report discrepancies.

## Data and Interpretation Boundaries

The representative CSV is distinct from the founder's original 12-year personal observation archive.

The validator checks structural properties of longitudinal records. It does not establish medical causation, clinical validity, or recovery outcomes.

The preservation of chronology, continuity, context, and provenance is the central purpose of the CS-NRRM™ framework.

## Licensing and Use

Use of this software and related materials is subject to the applicable license and official CS-NRRM™ usage policies.

Do not assume that public availability grants unrestricted commercial implementation, redistribution, or licensing rights.

Consult the official project repository and usage policy before reuse.

## Official References

**Website:** https://www.cs-nrrm.com

**GitHub:** https://github.com/changhunshin-csnrrm/cs-nrrm

**Founder:** Changhun Shin

**ORCID:** 0009-0001-3805-3023

---

*CS-NRRM™ observes time through continuity-preserved longitudinal records. Software validation results should not be interpreted as medical or clinical evidence.*
