# CS-NRRM™ Validator v2.2 — Comparison Demo v1.0

**Date:** 2026-11-24  
**Status:** Locally executed on Windows; results transcribed from user-provided terminal screenshots.  
**Scope:** Non-medical, non-clinical structural validation of a public representative CSV.  
**Evidence status:** Execution screenshots reviewed in conversation. Original local JSON result files and CSV bytes were **not** provided for independent file-level inspection in this report; local SHA-256 values remain to be collected.

## 1. Objective and design

Compare a deliberately limited basic-CSV CONTROL with CS-NRRM™ Validator v2.2 on (a) an unchanged representative dataset and (b) a copy with one intentionally injected adjacent chronological inversion. This is a **capability demonstration**, not a comparison against all conventional ETL or longitudinal validation systems.

- Source: `representative_observation_sample.csv`, 585 representative observations. This is **not** the complete private 12-year archive and not independently established ground truth.
- CONTROL: `control_basic_csv.py` (v1.0.0), which checks CSV structure, required fields, duplicate IDs, timestamp validity, and permitted confidence values; it **does not** check chronological order or observation links.
- Framework: `validate_csnrrm_v2_2.py` (v2.2.0), which additionally checks ID/sequence ordering, previous/next links, definite chronological inversions, and counts ambiguous/overlapping time intervals.
- Probe generator: `create_chronology_probe.py`, which creates a separate CSV and manifest without modifying the original source.

## 2. Observed execution results

| Input | CONTROL reported issues | CS-NRRM v2.2 reported issues | Records |
|---|---:|---:|---:|
| Original representative CSV | 0 | 0 | 585 |
| Injected chronology probe CSV | 0 | 1 `definite_chronological_inversion` | 585 |

The probe generator reported exchanging `observation_date` and `observation_time` between **CSNRRM-OBS-0005** and **CSNRRM-OBS-0006**. It reported that the original source was not modified. The validator's observed issue count was `{"definite_chronological_inversion": 1}`.

The original v2.2 run also reported the following **descriptive counts, not errors**:

| Metric | Original CSV | Probe CSV |
|---|---:|---:|
| Temporally ambiguous adjacent pairs | 34 | 32 |
| Overlapping all-record pairs, including ties | 432 | 432 |
| Year-only dates | 34 | 34 |
| Unknown observation time | 36 | 36 |
| Unknown region | 49 | 49 |
| Identical-timestamp adjacent pairs | 2 | 2 |
| Identical-timestamp all-record pairs | 3 | 3 |
| Confidence high / medium / low | 503 / 48 / 34 | 503 / 48 / 34 |

Temporal overlap and ambiguity are not themselves ordering errors. The counts above are as displayed in the terminal screenshots; they have not been independently recomputed here.

## 3. Interpretation

The injected inversion was **not flagged by the deliberately limited CONTROL** because it lacks a chronology comparison rule. CS-NRRM v2.2 **flagged one definite adjacent inversion** on the same probe input. This confirms the observed response of this implementation to this selected mutation in the local execution.

This does **not** establish that CS-NRRM is technically unique, superior to well-configured ETL tools, independently certified, clinically valid, or generally correct for other datasets. An ordinary program implementing the same chronological comparison can detect this error. The two test arms have deliberately different checking scopes.

The validator's row-derived IDs and links do not establish continuity in the private archive. It does not prove source provenance or truth, diagnose or treat conditions, or predict outcomes.

## 4. Preservation and reproducibility

Keep these files together in `Comparison_Demo_v1`:

- `representative_observation_sample.csv` — original representative source; **do not modify**.
- `validate_csnrrm_v2_2.py` — original copied validator; **do not modify**.
- `control_basic_csv.py` — limited CONTROL.
- `create_chronology_probe.py` — controlled mutation generator.
- `chronology_probe_v1.csv` — generated probe.
- `chronology_probe_manifest_v1.json` — change log with source and probe SHA-256.
- `control_original_result_v1.json` — normal CONTROL output, to be regenerated.
- `control_probe_result_v1.json` — probe CONTROL output, to be regenerated.
- `csnrrm_result_v2_2.json` — original CS-NRRM output.
- `csnrrm_chronology_probe_result.json` — probe CS-NRRM output.
- `Comparison_Demo_v1_Report.md` — this report.
- `Comparison_Demo_v1_SHA256SUMS.txt` — hashes to be generated locally.

**Preservation caveat:** During the experiment, the second CONTROL run wrote to the default `control_result_v1.json`, overwriting the original CONTROL result. The source CSV was not affected. The provided `preserve_comparison_results.bat` reruns both CONTROL checks using distinct output filenames, then computes local hashes. It does not change either source CSV or the validator code.

## 5. Verification still pending

1. Collect the regenerated CONTROL outputs and local SHA-256 manifest.
2. Verify file hashes and compare `source_sha256` in the probe manifest against the source CSV hash.
3. If publishing, include the relevant original output JSON files and the exact script versions; preserve the distinction between screenshot-observed results and independently re-executed verification.

**Conclusion:** A single intentionally injected chronological inversion was reported by CS-NRRM Validator v2.2 but not by a limited basic CSV CONTROL, on 585 public representative observations in the user's Windows execution. This is a narrow, reproducible structural-software demonstration, not external independent validation.
