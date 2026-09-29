# D02 operational resource plan — 2026-09-25

Dataset: selected FAFB v783 product set in `docs/decisions.md`; input metadata in `docs/data_candidate.md`. These limits cover **acquisition and bounded inspection**, not the final experiment/training budget.

| Item | Basis / cap |
| --- | --- |
| Free disk at measurement | 103.03 GiB on C:, from .NET `DriveInfo`; recheck immediately before each download |
| Published raw input total | 897,005,420 bytes (~0.835 GiB): three core files plus one 16,853,770-byte auxiliary aggregate |
| Per-file download ceiling | 1,000,000,000 bytes, above the largest published file of 852,022,274 bytes |
| Total selected download ceiling | 1,200,000,000 bytes |
| Minimum free disk after an acquisition | 80 GiB, leaving at most ~23 GiB of the measured free disk for this project and drift |
| Processing memory target | 4 GiB peak; use Arrow batches of at most 50,000 rows and at most 4 workers |
| Temporary / derived / pilot-run allocations | 4 / 5 / 5 GiB respectively; these are ceilings to enforce in downstream jobs, not measured expected use |

The selected raw files (~0.835 GiB), a same-size temporary partial download for the largest file (~0.794 GiB), the 4 GiB temporary allocation, 5 GiB derived allocation, and 5 GiB pilot-run allocation total about **15.63 GiB** if all reserved at once. The original 103.03 GiB free-space measurement predated acquisition. A new measurement on 2026-09-26 was **94.26 GiB free**, leaving only 14.26 GiB above the 80 GiB floor for future writes. Recheck free space and lower future simultaneous allocations before a pilot or another large acquisition; the current auxiliary download itself stayed within the floor. The downloader streams and enforces the floor.

The .NET runtime reported 15.93 GiB `TotalAvailableMemoryBytes` and 12 logical processors. This is not a physical-RAM measurement. `Get-CimInstance` was denied, so enforce the 4 GiB process cap through job design and measurement, and reduce batch size if a pilot exceeds it. No full-graph or final-training job is authorized by this plan. The final seed/training budget remains `ISSUE-004` until pilot variance and cost are measured.

The numeric caps are operational choices, not a claim about biological parameters. If `configs/resources.yaml` changes, record the reason and affected runs in `docs/protocol_changes.md`.
