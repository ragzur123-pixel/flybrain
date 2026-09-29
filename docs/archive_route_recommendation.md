# Proposed P1 repair: use the publication-time v783 archive as the baseline

Status: **selected by Rüzgar on 2026-09-28; archive-specific P1 gate passed**
in `docs/p1_archive_gate_review_2026-09-28.md`. This is not a frozen circuit or
protocol. Prepared 2026-09-26 after the ten Codex mismatches and an
archive-family aggregate check.

## Why this route fits the question

The project asks whether a reduced connectome-derived controller can perform
and recover under controlled perturbations. It does not require matching the
present-day Codex service. The 2024 FlyWire paper and its v783.0 Zenodo deposit
form a citable, immutable publication-time baseline. The three core files have
published checksum and local integrity evidence; the auxiliary presynaptic
aggregate is from that same deposit (FW-015–FW-017, FW-044–FW-046, FW-055).
Current Codex FAFB v783 displays the same checked directions and neuropil
names, but all ten checked pair counts differ (FW-053). The Codex FAQ explicitly
allows current files to differ from original archives (FW-052), and About
FlyWire documents a newer synapse detector (FW-054). The latter is a plausible
contributor, not a proven explanation of each delta.

## Evidence already obtained

1. `data/raw/manifest.csv` pins four local files, including the aggregate,
   with byte counts, source URLs, download times, and SHA-256 values. Acquisition
   matched the publisher's MD5 or Git-blob checksum.
2. `data/derived/full_validation.json` records a full integrity scan of the
   proofread connection file. It was rerun after the fourth product was added;
   its manifest-hash list covers all four products.
3. `data/derived/manual_pair_raw_audit.json` independently rescanned the
   16,847,997-row file for the ten preselected directed pairs and reverse
   directions; it agreed with the exploratory screen.
4. `data/derived/archive_aggregate_check.json` compares the graph with the
   same release's independent presynaptic summary for 19 candidate neurons.
   All 56 comparable neuron/region subtotals obey the expected upper bound;
   two `UNASGD` rows have no counterpart because that region is absent from
   the entire aggregate product. This is partial consistency evidence, not
   exact pair verification.
5. `docs/codex_reconciliation.md` preserves the ten current-service mismatches
   as a separate version comparison. No current Codex weights have been
   mixed into the publication-time graph.

## Proposed revised P1 acceptance rule

Rüzgar selected the publication-time archive on 2026-09-28. The P1 manual-check
criterion now validates **release provenance and
internal consistency**, while reporting current Codex as a different
derivative. Require all of these before P1 passes:

- The three Zenodo v783.0 files and the authors' compatible annotation tag
  `v2.1.0` each have publisher checksum or Git-blob ID plus local SHA-256/size
  checks; the full validator has scanned the graph after the manifest
  expansion. Do not describe the annotation TSV as a Zenodo file.
- Ten preselected pair rows are reproducible from the immutable raw file; IDs,
  direction, region, and aggregation are checked by the independent raw-row
  audit. This is a software reproducibility check, not a second anatomical
  measurement.
- The auxiliary aggregate bound passes for every region that both products
  represent. Record `UNASGD` as an explicit coverage exception and verify that
  it does not affect any of the ten chosen pair rows. The current raw audit
  confirms zero `UNASGD` rows among those ten pairs.
- The difference from current Codex is disclosed, with both data products and
  their dates named. No assertion that the ten count deltas were fully caused
  by a specific detector is allowed.
- Pair threshold, neurotransmitter handling, right DNp28 `outlier_seg`, and
  final root-ID set remain later explicit decisions. Passing P1 would permit
  P2 circuit selection, not approve a circuit or simulation result.

## Alternative

Selecting current Codex as baseline may give a graph consistent with the
current portal, but it requires reviewing the catalog agreement, inspecting
actual products and terms, downloading a coherent set, revalidating its schema
and hashes, and repeating the circuit screen. The present ten per-cell exports
are insufficient to reconstruct a whole graph. Neither route should be called
complete until its own acceptance checks pass.

| Baseline | Best fit | Immediate work | Main limitation |
| --- | --- | --- | --- |
| Publication-time v783 archive | Reproducing a paper-aligned, checksum-pinned experiment whose graph and annotations share a release lineage | Confirm the revised provenance/internal-consistency gate and record the owner's selection | Current Codex connection counts will not match this historical graph |
| Current Codex FAFB v783 service | Comparing directly with values shown by today's portal or studying its current processing | Review catalog terms, acquire a coherent full graph and annotations, then repeat validation and circuit screening | Product set and revised counts are not yet pinned here; ten per-cell CSVs cannot replace the graph |

For FlyAI's planned controlled recovery experiment, the archive has the
stronger reproducibility and schedule fit. A separate current-Codex comparison
can remain an exploratory sensitivity analysis after the core protocol works.

**Selected route:** the publication-time archive for a reproducible
paper-aligned baseline, subject to the revised P1 gate.
The expected benefit is a bounded, testable project path; the limitation is
that the model will represent the original release, not current Codex counts.

Visual preview: `figures/archive_aggregate_check.png` (archive subset-bound
result only; the separate five-check P1 review records the gate pass).
