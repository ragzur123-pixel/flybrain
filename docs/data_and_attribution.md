# Data and attribution

FlyAI uses the publication-time [FlyWire Consortium FAFB v783.0 connectivity archive](https://zenodo.org/records/10676866) (DOI: 10.5281/zenodo.10676866) with a pinned annotation product. Product URLs, downloaded byte counts, and SHA-256 hashes are in `configs/data_sources.json` and `data/raw/manifest.csv`. The selected archive is distinct from values currently shown by the Codex service; [the reconciliation note](codex_reconciliation.md) records ten checked differences. Do not combine their edge weights.

The [FlyWire public-release guidelines](https://home.flywire.ai/guidelines) state CC BY-NC 4.0 terms and provide citation guidance. The selected Zenodo record's rights display is less explicit. This project conservatively treats source-derived material as noncommercial and attributed; see the [P0 gate review](p0_gate_review.md) for the recorded basis and limits. This statement does not assign a license to independently written code.

The repository does not contain the 852 MB raw connection file, other raw downloads, or local derived tables. These remain local so a public clone is small and does not redistribute the source products. The manifest identifies the exact inputs used for checks. Figure captions and methods must identify whether an image is generated from archive data, a synthetic software fixture, or an experiment. A copied paper figure is not a project-generated figure and is not included here.

Before reusing a figure or publishing new data products, check the current source terms and cite the FlyWire Consortium archive and any annotation source used for that specific product. The source ledger in `docs/sources.md` records the paper and annotation references used in the research notes.
