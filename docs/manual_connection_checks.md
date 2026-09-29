# P1 manual FlyWire/Codex connection checks

Status: **superseded draft; no Codex checks performed**. The current, broader packet is
`docs/manual_connection_checks_v2.md`. This original DNp20-focused selection is retained
for provenance. These ten ordered pairs were selected
deterministically from the full v783 local path screen. The values below are local
pair-summed synapse counts across neuropil rows, not portal observations.

Source: `data/derived/ocellar_path_screen.json`; selector: `src/flyai/prepare_manual_checks.py`.
Use FAFB v783 in Codex. For each pair, inspect the presynaptic cell's outputs
or the postsynaptic cell's inputs. Record the displayed direction, count, page
or screenshot reference, and any difference in the blank review columns. Codex
may apply its display threshold or an aggregation rule different from this file.
Do not mark a row reconciled merely because the local values look plausible.

| # | Pre root ID | Post root ID | Local roles/sides | Local pair synapses | Neuropil rows | Codex direction/count | Lookup evidence | Result |
| ---: | --- | --- | --- | ---: | ---: | --- | --- | --- |
| 1 | 720575940630424631 | 720575940627972485 | photoreceptor (left) → OCG01 (left) | 37 | 1 | pending | pending | pending |
| 2 | 720575940613652906 | 720575940621734126 | photoreceptor (left) → OCG01 (left) | 24 | 1 | pending | pending | pending |
| 3 | 720575940640123299 | 720575940630751031 | photoreceptor (right) → OCG01 (right) | 26 | 1 | pending | pending | pending |
| 4 | 720575940621229409 | 720575940631622393 | photoreceptor (right) → OCG01 (right) | 21 | 1 | pending | pending | pending |
| 5 | 720575940607293570 | 720575940621202670 | photoreceptor (center) → OCG01 (left) | 16 | 1 | pending | pending | pending |
| 6 | 720575940618156628 | 720575940622318085 | photoreceptor (center) → OCG01 (right) | 16 | 1 | pending | pending | pending |
| 7 | 720575940621202670 | 720575940629390123 | OCG01 (left) → DNp20 (left) | 242 | 2 | pending | pending | pending |
| 8 | 720575940628416232 | 720575940629390123 | OCG01 (left) → DNp20 (left) | 178 | 2 | pending | pending | pending |
| 9 | 720575940631187287 | 720575940644166048 | OCG01 (right) → DNp20 (right) | 240 | 2 | pending | pending | pending |
| 10 | 720575940615097490 | 720575940644166048 | OCG01 (right) → DNp20 (right) | 125 | 2 | pending | pending | pending |

## Reconciliation rule

Mark a check as matched only after an independent Codex v783 view confirms
the ordered pre→post pair and its displayed synapse total under an equivalent
aggregation/filter. Document any portal mismatch rather than changing the raw
count. The P1 gate stays open until all ten checks are documented or discrepancies
are explained and resolved.
