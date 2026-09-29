# FAFB v783 data lineage and acquisition record

Date checked: 2026-09-25. Status: **selected for validation** in `docs/decisions.md`. All three products have been downloaded and checksum verified; actual schema and bounded join observations are in `docs/data_validation.md`. The graph and circuit are not yet validated for experiments.

## Proposed product set

| Role | Official product and location | Published size | Published integrity identifier | Planned raw path |
| --- | --- | ---: | --- | --- |
| Directed, weighted proofread connections | [Zenodo v783.0 `proofread_connections_783.feather`](https://zenodo.org/api/records/10676866/files/proofread_connections_783.feather/content) | 852,022,274 bytes | MD5 `f48f972d262323a102aed49af1396b8a` | `data/raw/proofread_connections_783.feather` |
| Proofread root-ID membership | [Zenodo v783.0 `proofread_root_ids_783.npy`](https://zenodo.org/api/records/10676866/files/proofread_root_ids_783.npy/content) | 1,114,168 bytes | MD5 `e0e6c19732fd8c7a4e39a2d170105421` | `data/raw/proofread_root_ids_783.npy` |
| Neuron class, flow, neurotransmitter, and other annotations | [Authors' `v2.1.0` neuron TSV](https://raw.githubusercontent.com/flyconnectome/flywire_annotations/v2.1.0/supplemental_files/Supplemental_file1_neuron_annotations.tsv) | 27,015,208 bytes | Git blob SHA `1a3168731618ee62a47392252d3af7664e739e9e`; tag commit `ebd66db2596fcc39c6950fb54ea3efa00f7fe8a0` | `data/raw/Supplemental_file1_neuron_annotations_v2.1.0.tsv` |

The first two files total **853,136,442 bytes** (~0.795 GiB); all three total **880,151,650 bytes** (~0.820 GiB). These are published metadata, not observed local files. The annotation authors directly link the connectivity archive and identify tag 2.1.0 with v783 and the 2024 papers (FW-034). The archive says its connection table has one row per directed neuron pair **and neuropil**, with `syn_count` and averaged neurotransmitter probabilities (FW-015–FW-017). A pair may therefore occupy multiple rows; aggregation policy is still a scientific decision. The Codex viewer's five-synapse display minimum must not be silently imposed on this archive.

## Rights and attribution

The archive API says CC BY 4.0 and open access (FW-035). FlyWire's public-release guideline describes v783 data, including annotations, as CC BY-NC 4.0 (FW-007), while the archive page itself renders an empty license field (FW-031). The authors' annotation repository has no API license identifier or license file in the tagged tree (FW-038). For a **noncommercial** research project, use the stricter intersection: credit the FlyWire Consortium and relevant Dorkenwald/Schlegel papers, link the source record and license, identify transformations, and avoid commercial use. Derived figures/tables in an attributed report appear compatible with the public-release guideline and Zenodo metadata; this is a license reading, not a product-specific grant. Do not redistribute source files or publish a derived raw-scale graph until the apparent license difference and annotation-repository terms are resolved. The attribution wording and any neurotransmitter-source citation will be finalized after the actual columns used are known (FW-009).

## Local capacity snapshot

Read-only measurements on 2026-09-25 using `[System.IO.DriveInfo]::new('C')`, `[Environment]::ProcessorCount`, and `[System.GC]::GetGCMemoryInfo()`:

| Quantity | Observed value | Interpretation |
| --- | ---: | --- |
| C: free | 103.03 GiB | Snapshot; OneDrive synchronization and other processes can change it. |
| C: total | 463.67 GiB | Physical drive size reported by .NET. |
| Logical processors | 12 | Not a sustained compute budget. |
| GC `TotalAvailableMemoryBytes` | 15.93 GiB | Process-available memory estimate, not confirmed physical RAM or safe job limit. |

`Get-CimInstance` was denied in this sandbox, so physical RAM and CPU model remain unmeasured. The three selected downloads occupy under 1 GiB of published bytes. `configs/resources.yaml` and `docs/resource_plan.md` now hold acquisition and bounded-inspection caps; `src/flyai/acquire.py` enforced the download limits. A full simulation/training budget still requires a pilot under `ISSUE-004`.

## Validation sequence after selection

1. **Done:** obtained all three pinned products without overwrite; recorded bytes and local SHA-256 in `data/raw/manifest.csv`, and matched Zenodo MD5/Git-blob SHA-1. The Git blob SHA is not a file SHA-256.
2. **Partial:** inspected real Arrow/NumPy/TSV schemas, the full annotation/root-ID join, and a bounded 196,608-row connection sample (`docs/data_validation.md`). Full duplicate, null, ID, and weight checks remain.
3. Define a predeclared rule for aggregating neuropil rows and for any connection threshold. Record the source and rationale in `docs/decisions.md` and `docs/protocol_changes.md` before circuit scoring.
4. Validate candidate input/output classes against primary biology, actual v783 annotation rows, and graph reachability. An annotated class or descending neuron is not itself proof of a motor-command mapping.

Open questions: `ISSUE-001` circuit and IDs; `ISSUE-002` observed schema, hashes, and terms; `ISSUE-003` model/sign mapping; `ISSUE-004` resource caps.
