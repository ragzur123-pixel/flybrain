# P1 archive-specific gate review — 2026-09-28

**Decision: PASS for the publication-time 2024 FAFB v783 archive selected by
Rüzgar on 2026-09-28.** This supersedes the 2026-09-26 failed gate for choosing
a main graph product. It does not make current Codex connection counts equal
to archive counts, validate a final circuit, or establish behavior.

The acceptance rule is the provenance/internal-consistency route in
`docs/archive_route_recommendation.md`: one immutable release family, ten
preselected archive pair rows reproducible from raw bytes, a bounded
same-release aggregate comparison with explicit coverage exceptions, and
disclosure of the current-service difference. The rule was chosen before
any vehicle score or final circuit selection.

| Required archive check | Result | Evidence |
| --- | --- | --- |
| Four pinned compatible products, published checksum/Git-blob metadata, and local SHA-256/size checks | PASS | `configs/data_sources.json`, `data/raw/manifest.csv`, acquisition record in `docs/data_validation.md`; three Zenodo v783.0 products plus the authors' annotation tag `v2.1.0`, not four Zenodo files |
| Complete graph integrity after the four-product manifest | PASS | `.venv\Scripts\python.exe src\flyai\validate_raw.py --workspace .` exited 0 on 2026-09-28; `data/derived/full_validation.json`: 16,847,997 rows, 258/258 batches, zero duplicate pair/neuropil rows, zero nonpositive counts, zero IDs absent from proofread list; 161.2 s and 1,009,696,768 peak RSS bytes |
| Ten preselected directed pairs reproducible from the archive | PASS | `.venv\Scripts\python.exe src\flyai\audit_manual_pairs.py --workspace .` exited 0; ten ordered pairs, 16,847,997 rows rescanned, pair totals and neuropil rows match the earlier screen; `data/derived/manual_pair_raw_audit.json` |
| Same-release aggregate consistency with coverage exceptions | PASS within its scope | `.venv\Scripts\python.exe src\flyai\check_archive_aggregate.py --workspace .` exited 0; 19 IDs, 56/56 comparable rows obey proofread subtotal ≤ all-partner total, two `UNASGD` rows not comparable, no selected pair row in `UNASGD`; `data/derived/archive_aggregate_check.json` |
| Current Codex difference disclosed without mixing weights | PASS | `docs/codex_reconciliation.md`: 0/10 pair totals match current Codex; its FAQ permits current/publication differences, but no exact cause of each delta is established (FW-052–FW-054) |

`src/flyai/review_archive_gate.py` reconciled the saved reports and manifest:
all five machine checks passed and the result was saved to
`data/derived/p1_archive_gate_check.json` (exit 0). The complete unittest
suite passed 18 tests (exit 0), including two gate-invariant tests. These
tests verify software consistency, not independent biological measurements.

## Scope and remaining limits

- The presynaptic aggregate provides an upper bound for comparable regions;
  it is not an exact second measurement of each ordered pair. Its absent
  `UNASGD` region is reported explicitly.
- The current Codex service remains a separate product. Its ten observed
  count differences need no edge-by-edge causal explanation for this archive
  baseline, but must be disclosed in any methods/report comparison.
- The threshold, final root IDs, right DNp28 `outlier_seg` status,
  neurotransmitter sign assumptions, side-aware sensor mapping, and virtual
  motor decoder belong to P2/P4. No simulation or final run exists.
- P1 pass allows the C01–C07 circuit-selection work; it does not pass P2.
