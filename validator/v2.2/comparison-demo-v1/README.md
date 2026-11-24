# CS-NRRM™ Validator v2.2 — Comparison Demo v1.0

Date: 2026-11-24
Execution environment: Local Windows PC
Scope: Non-medical structural software demonstration

## Purpose

This demonstration compares a deliberately limited basic CSV CONTROL with CS-NRRM™ Validator v2.2 using the same 585 public representative observation records.

## Method

1. Run both programs on the unchanged representative CSV.
2. Create a separate probe CSV by swapping date/time values between two adjacent records (CSNRRM-OBS-0005 and CSNRRM-OBS-0006).
3. Run both programs on the modified probe CSV.
4. Preserve outputs, the modification manifest, and SHA-256 checksums.

## Observed results

| Dataset | Basic CONTROL | CS-NRRM Validator v2.2 |
| --- | --- | --- |
| Original 585 records | 0 reported issues | 0 reported issues |
| Modified 585 records | 0 reported issues | 1 definite chronological inversion |

The validator also reports temporal ambiguity and uncertainty counts. Overlapping time intervals are not automatically errors.

## Evidence boundaries

- The CONTROL intentionally does not check chronological ordering or record links. It does not represent all conventional data-engineering approaches.
- The inversion was deliberately introduced; it was not discovered in the original data.
- The 585 records are public representative demonstration data, not the full private 12-year archive or independently established ground truth.
- Results were executed locally by the founder and are not independent third-party certification.
- This does not demonstrate clinical validity, medical outcomes, general software superiority, or commercial value.
- The original Validator v2.2 implementation and source CSV were not modified.

## Reproduction evidence

The accompanying report, scripts, original and modified CSVs, JSON outputs, and SHA-256 manifest document the local comparison. The Windows SHA-256 recheck reported 11 checked files, zero mismatches, and PASS.

See `Comparison_Demo_v1_Report.md` and `Comparison_Demo_v1_SHA256SUMS.txt` for details.
