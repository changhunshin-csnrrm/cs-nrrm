# CS-NRRM™ External Dataset Structural Mapping — UQ Longitudinal Skin Image Dataset

## Status

Publication-Level External Dataset Structural Mapping

This document presents a publication-level structural comparison between the CS-NRRM™ continuity-preserved structural observation approach and the publicly documented organization of an independently created longitudinal dataset.

This is not an independent validation of CS-NRRM™ and does not imply endorsement, collaboration, or validation by the University of Queensland, Scientific Data, or the original dataset authors.

---

## External Data Source

This demonstration references the source publication and public metadata describing the independently created dataset. The original dataset files, complete CSV metadata, and source-level records were not downloaded or processed:

**Ghahari, N., Caffery, L., Betz-Stablein, B., et al. (2025).**  
*A longitudinal dataset of tile and corresponding dermoscopic images with metadata for identifying skin cancers.*

**Dataset Publisher:** The University of Queensland  
**Dataset DOI:** 10.48610/a13deaf

**Publication:** Scientific Data, Volume 12, Article 1602 (2025)  
**Publication DOI:** 10.1038/s41597-025-05880-2

The source dataset and publication were created independently of CS-NRRM™.

CS-NRRM™ was not involved in the creation, collection, labeling, publication, or validation of the source dataset.

The dataset is referenced here solely as an external public data source for demonstrating structural mapping of longitudinal observations.

---

## Source Dataset Structure

The University of Queensland dataset is organized around repeated observations of the same skin lesions across multiple study visits.

According to the source publication, the dataset includes:

- participant identifiers
- lesion identifiers
- repeated visit identifiers
- dermoscopic image identifiers
- tile image identifiers
- anatomical location metadata
- capture-device information
- repeated longitudinal observations across 2 to 7 timepoints
- linked metadata tables connecting images and observation context

The source dataset already contains longitudinal relationships. CS-NRRM™ does not claim to create or discover those relationships.

The purpose of this demonstration is to test whether those existing longitudinal relationships can be represented within the CS-NRRM™ continuity-preserved structural observation approach.

---

## CS-NRRM™ Structural Mapping

The source dataset elements are mapped to CS-NRRM™ structural elements as follows:

| UQ Source Element | CS-NRRM™ Structural Element | Structural Role |
|---|---|---|
| Participant ID | Subject Reference | Preserves identity of the observation subject |
| Lesion ID | Observation Target | Preserves continuity of the same observed target across time |
| Visit ID | Timepoint | Represents the temporal position of each observation |
| Dermoscopic Image ID | Observation Reference | Links a specific observation artifact to a timepoint |
| Tile Image ID | Observation Reference | Preserves corresponding visual context at another imaging scale |
| Anatomical Location | Observation Context | Preserves spatial/anatomical context |
| Capture Device / Camera | Capture Context | Preserves acquisition context |
| Repeated Visits | Chronology | Preserves original temporal ordering |
| Same Lesion Across Visits | Continuity Relationship | Connects repeated observations of the same target |
| Dataset DOI / Publication DOI | Provenance | Preserves external source attribution |
| Diagnostic / Clinical Metadata | Source Metadata | Retained as source information without CS-NRRM™ medical interpretation |
| CS-NRRM™ Boundary Rules | Interpretation Boundary | Prevents diagnosis, treatment, causal, or predictive interpretation |

---

## Structural Flow

**External UQ Longitudinal Dataset**

↓  

**Participant → Lesion → Visit → Image / Metadata**

↓

**CS-NRRM™ Structural Mapping**

↓

**Chronology + Continuity + Observation Context + Capture Context + Provenance + Interpretation Boundary**

↓

**Continuity-Preserved Machine-Readable Representation**

---

## Mapping Principle

CS-NRRM™ does not alter the original chronological order or source identity of the UQ dataset.

The mapping preserves:

- source provenance
- participant-level reference
- lesion-level continuity
- visit-level chronology
- observation context
- capture context
- original source metadata
- explicit non-medical interpretation boundaries

This demonstration is intended to test structural portability of the CS-NRRM™ approach to independently created longitudinal data.

It does not test clinical validity, diagnostic performance, treatment outcomes, or predictive accuracy.

---

## External Longitudinal Sequence Demonstration

The source publication provides representative examples of the same skin lesion observed repeatedly across multiple study visits.

Figure 3 of the Scientific Data publication presents longitudinal examples using the following visit structure:

**Visit 1 — Baseline**  
↓  
**Visit 2 — 6 months**  
↓  
**Visit 3 — 12 months**  
↓  
**Visit 4 — 18 months**  
↓  
**Visit 5 — 24 months**  
↓  
**Visit 6 — 30 months**  
↓  
**Visit 7 — 36 months**

The figure includes corresponding dermoscopic and tile-image observations across these repeated timepoints for representative lesions.

Source figure:

**Scientific Data — Figure 3**  
https://www.nature.com/articles/s41597-025-05880-2/figures/3

---

## CS-NRRM™ Representation of the Sequence

For this demonstration, the published longitudinal sequence is treated as an externally created observation sequence.

CS-NRRM™ represents the sequence structurally as:

| Structural Element | External Sequence Representation |
|---|---|
| Observation Target | Same lesion across repeated visits |
| Timepoint 1 | Baseline |
| Timepoint 2 | 6 months |
| Timepoint 3 | 12 months |
| Timepoint 4 | 18 months |
| Timepoint 5 | 24 months |
| Timepoint 6 | 30 months |
| Timepoint 7 | 36 months |
| Chronology | Original visit order preserved |
| Continuity | Same observation target maintained across time |
| Observation Context | Repeated skin-lesion observation |
| Imaging Context | Dermoscopic and tile-image representations |
| Provenance | University of Queensland dataset and Scientific Data publication |
| Interpretation Boundary | Structural representation only; no diagnostic or predictive interpretation |

---

## What This Demonstration Shows

This external-data demonstration shows that the CS-NRRM™ structural observation approach can represent a longitudinal sequence that:

- was not created by the founder of CS-NRRM™
- was independently collected and published by an external research group
- contains repeated observations of the same target
- contains explicit temporal ordering
- preserves longitudinal continuity across multiple timepoints
- can be mapped while retaining source provenance and observation context

The demonstration therefore provides evidence of **structural portability to an independently created longitudinal dataset**.

---

## What This Demonstration Does Not Show

This demonstration does not establish:

- independent validation of CS-NRRM™
- endorsement of CS-NRRM™ by the University of Queensland or the original authors
- clinical validity
- diagnostic accuracy
- treatment-effect evaluation
- causal interpretation
- predictive performance
- population-level generalization
- large-scale software scalability
- operational API or production infrastructure

The demonstration is limited to structural mapping of an externally created longitudinal observation sequence.

---

## Source Attribution and Independence

### Source Dataset

Ghahari, N., Caffery, L., Betz-Stablein, B., et al. (2025).  
*A longitudinal dataset of tile and corresponding dermoscopic images with metadata for identifying skin cancers.*

**Publisher:** The University of Queensland  
**Dataset DOI:** https://doi.org/10.48610/a13deaf

The source dataset is publicly documented as an independently created longitudinal skin-image dataset.

---

### Source Publication

Ghahari, N., Caffery, L., Betz-Stablein, B., et al. (2025).  
*A longitudinal dataset of tile and corresponding dermoscopic images with metadata for identifying skin cancers.*

**Scientific Data, 12, 1602 (2025)**  
**Publication DOI:** https://doi.org/10.1038/s41597-025-05880-2

**Figure 3:**  
https://www.nature.com/articles/s41597-025-05880-2/figures/3

---

## Attribution and Re-use

The University of Queensland dataset is identified by its source record as Open Access with permitted re-use subject to acknowledgement of the original dataset.

Any use of source dataset materials must follow the terms specified by the original data provider.

This CS-NRRM™ document does not redistribute the original dataset or claim ownership of the source images, metadata, labels, or research findings.

The original dataset remains the work of its respective creators and publisher.

---

## Independence Statement

The University of Queensland, Scientific Data, and the original authors are not affiliated with CS-NRRM™ through this demonstration.

They did not create, validate, endorse, review, or approve the CS-NRRM™ framework or this structural mapping.

CS-NRRM™ is applied here independently by Changhun Shin solely as a structural mapping demonstration using publicly documented external longitudinal data.

---

## Demonstration Status

**Current Status:** External Public Dataset Structural Mapping Demonstration

**Evidence Level:** Publication-level structural mapping

This demonstration is based on longitudinal structures and representative sequences explicitly documented in the source publication.

It does not yet constitute a record-level implementation using the complete source CSV metadata or original dataset files.

A future record-level implementation may be conducted if the source metadata and corresponding longitudinal records are directly processed within the CS-NRRM™ structure.

---

## Conclusion

This demonstration provides a documented example of applying the CS-NRRM™ continuity-preserved structural observation approach to a longitudinal dataset created independently of CS-NRRM™.

The demonstration supports the portability of the structural representation beyond the founder's original longitudinal archive while remaining limited to structural mapping.

It does not establish independent validation, clinical validity, predictive performance, or operational infrastructure deployment.
