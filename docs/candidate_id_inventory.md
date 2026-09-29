# C02 full candidate-ID provenance — 2026-09-28

Status: **all 291 annotation-derived candidate IDs inventoried and
checked for proofread-array membership; no subnetwork selected**.
The complete per-ID table is `data/derived/candidate_id_inventory.csv`.
This is a local archive inventory, not functional validation or
independent current-Codex reconciliation.

- Dataset: publication-time 2024 FAFB v783 archive; annotation tag `v2.1.0`.
- Annotation TSV SHA-256: `30be6c73975a70c56d930e27911f36455d3886e15abf383b78edd2a5d679e0b6`.
- Proofread-ID array SHA-256: `7c7b7e818e9232e5ab64793d52ba20574dbe9da3a6509fbc74193b0f259a01be`.
- Every CSV row records the source annotation field, exact type strings,
  biological side, status, annotation position, and proofread membership.

| Candidate role | Left | Right | Center | Total |
| --- | ---: | ---: | ---: | ---: |
| photoreceptor | 100 | 97 | 76 | 273 |
| OCG01 | 6 | 6 | 0 | 12 |
| DNp20 | 1 | 1 | 0 | 2 |
| DNp22 | 1 | 1 | 0 | 2 |
| DNp28 | 1 | 1 | 0 | 2 |

Total: **291** unique IDs, all in the pinned proofread array.
Nonblank status flags: **1**; right DNp28
`720575940640142141` is `outlier_seg`. The CSV retains that row
rather than silently excluding it. A blank status is not a guarantee
of accurate segmentation or functional suitability.

C03 predeclared and checked path/threshold criteria before any vehicle
score. C04 selected the DNp20+DNp22 output family, so the flagged DNp28
cell is outside the [selected subnetwork](selected_subnetwork.md).
The config retains all qualifying biological-side paths with deterministic
ordering; virtual sensor encoding and motor decoding remain open.
