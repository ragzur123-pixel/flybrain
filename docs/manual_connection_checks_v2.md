# P1 manual FlyWire/Codex connection checks

Status: **ten Codex CSV checks completed; all ten counts discrepant**. These ordered pairs were selected
deterministically from the full v783 local path screen. The values below are local
pair-summed synapse counts across neuropil rows, not portal observations.
**2026-09-28 update:** Rüzgar selected the publication-time 2024 archive as
the main graph baseline. The ten archive pairs reproduced in a fresh raw-row
audit and contribute to the [archive-specific P1 pass](p1_archive_gate_review_2026-09-28.md).
The current Codex values below remain a separate, discrepant comparison; they
are not expected to numerically reconcile with the chosen historical archive.
This revision covers direct photoreceptor→DNp28 and OCG01-mediated DNp20/DNp22 routes
after the primary-paper review (FW-048–FW-051). Right DNp28 is flagged `outlier_seg`.

Source: `data/derived/ocellar_path_screen.json`; selector: `src/flyai/prepare_manual_checks.py`.
An independent local full-file rescan (`data/derived/manual_pair_raw_audit.json`) matched
all ten forward totals and row counts and recorded each reverse direction. This is
still **local-file evidence**, not an independent Codex observation. See the visual
preview in `figures/manual_pair_audit.png`.
The independent portal exports and their hashes are in
`data/derived/codex_portal_2026-09-26/manifest.csv`. Their reconciliation is
`docs/codex_reconciliation.md`; its newer preview is
`figures/codex_reconciliation.png`. No row is marked matched.
The provisional annotation and proofread-ID provenance for these pairs is in
`docs/candidate_id_packet.md`; it does not select the final circuit.
Use FAFB v783 in Codex. For each pair, inspect the presynaptic cell's outputs
or the postsynaptic cell's inputs. Record the displayed direction, count, page
or screenshot reference, and any difference in the blank review columns. Codex
may apply its display threshold or an aggregation rule different from this file.
Do not mark a row reconciled merely because the local values look plausible.

| # | Pre root ID | Post root ID | Local roles/sides | Local pair synapses | Neuropil rows | Codex direction/count | Lookup evidence | Result |
| ---: | --- | --- | --- | ---: | ---: | --- | --- | --- |
| 1 | 720575940630424631 | 720575940627972485 | photoreceptor (left) → OCG01 (left) | 37 | 1 | pre→post: 54 | [CSV](../data/derived/codex_portal_2026-09-26/720575940627972485.csv) | discrepancy +17 |
| 2 | 720575940640123299 | 720575940630751031 | photoreceptor (right) → OCG01 (right) | 26 | 1 | pre→post: 48 | [CSV](../data/derived/codex_portal_2026-09-26/720575940630751031.csv) | discrepancy +22 |
| 3 | 720575940607293570 | 720575940621202670 | photoreceptor (center) → OCG01 (left) | 16 | 1 | pre→post: 67 | [CSV](../data/derived/codex_portal_2026-09-26/720575940621202670.csv) | discrepancy +51 |
| 4 | 720575940618156628 | 720575940622318085 | photoreceptor (center) → OCG01 (right) | 16 | 1 | pre→post: 30 | [CSV](../data/derived/codex_portal_2026-09-26/720575940622318085.csv) | discrepancy +14 |
| 5 | 720575940618432769 | 720575940621561697 | photoreceptor (left) → DNp28 (left) | 15 | 1 | pre→post: 41 | [CSV](../data/derived/codex_portal_2026-09-26/720575940621561697.csv) | discrepancy +26 |
| 6 | 720575940632376204 | 720575940640142141 | photoreceptor (right) → DNp28 (right) | 35 | 1 | pre→post: 46 | [CSV](../data/derived/codex_portal_2026-09-26/720575940640142141.csv) | discrepancy +11 |
| 7 | 720575940621202670 | 720575940629390123 | OCG01 (left) → DNp20 (left) | 242 | 2 | pre→post: 355 | [CSV](../data/derived/codex_portal_2026-09-26/720575940629390123.csv) | discrepancy +113 |
| 8 | 720575940631187287 | 720575940644166048 | OCG01 (right) → DNp20 (right) | 240 | 2 | pre→post: 319 | [CSV](../data/derived/codex_portal_2026-09-26/720575940644166048.csv) | discrepancy +79 |
| 9 | 720575940629102891 | 720575940615043368 | OCG01 (left) → DNp22 (left) | 417 | 2 | pre→post: 482 | [CSV](../data/derived/codex_portal_2026-09-26/720575940615043368.csv) | discrepancy +65 |
| 10 | 720575940615097490 | 720575940631225996 | OCG01 (right) → DNp22 (right) | 314 | 2 | pre→post: 394 | [CSV](../data/derived/codex_portal_2026-09-26/720575940631225996.csv) | discrepancy +80 |

## Reconciliation rule

Mark a check as matched only after an independent Codex v783 view confirms
the ordered pre→post pair and its displayed synapse total under an equivalent
aggregation/filter. Document any portal mismatch rather than changing the raw
count. All ten checks are documented as discrepant; P1 stays open until the
source-product difference is explained and a consistent validation route is
selected. Do not silently substitute current Codex counts into the archive.
