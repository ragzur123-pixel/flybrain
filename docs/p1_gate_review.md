# P1 gate review — 2026-09-26

**Historical review:** Rüzgar selected the 2024 publication-time archive on
2026-09-28. The subsequent [archive-specific review](p1_archive_gate_review_2026-09-28.md)
passed its revised acceptance rule. The failed comparison below is preserved
to document why archive and current Codex counts must remain separate.

**Decision: FAIL; P2 circuit selection remains closed.**

| Required check | Result | Evidence |
| --- | --- | --- |
| One pinned FAFB v783 publication-time product set with manifest and hashes | PASS for the selected archive | `data/raw/manifest.csv`; `docs/data_validation.md`; FW-044 |
| Full local schema, ID membership, and connection integrity | PASS for the selected archive | `data/derived/full_validation.json`; FW-046 |
| Separate archive-family presynaptic aggregate | PARTIAL: 56 comparable region rows obey the subset bound; two `UNASGD` rows have no aggregate counterpart | `data/derived/archive_aggregate_check.json`; FW-055–FW-056 |
| Ten preselected ordered connection lookups in current Codex FAFB v783 | DONE; directions and neuropil rows observed | `docs/manual_connection_checks_v2.md`; ten hashed exports in `data/derived/codex_portal_2026-09-26/` |
| Pair synapse totals reconcile, or product differences are explained and resolved | **FAIL: 0/10 matched** | `docs/codex_reconciliation.md`; `data/derived/codex_reconciliation.json`; FW-052–FW-053 |
| One consistent graph product is ready for circuit extraction | **FAIL** | Publication-time archive and current Codex service differ; no source-product choice after this finding |

The discrepancy is an observed comparison between two distinct products that
share FAFB v783 root IDs. The [Codex FAQ](https://codex.flywire.ai/faq)
explicitly warns that current service downloads may differ from original
publication archives. It does not identify the precise processing step
responsible for these ten count changes. Its [About FlyWire page](https://codex.flywire.ai/about_flywire)
documents a newer synapse detector than the original release (FW-054), a
plausible contributor whose edge-by-edge effect has not been established.
Retain the archive and Codex exports
separately. Do not substitute one set of counts into the other or claim a
validated circuit based on their numerical agreement.

The next gate repair is a dated data-product decision. If current Codex is
selected, inspect its static catalog, citation terms, product sizes/schemas,
and a small sample before rehashing and validating a coherent file set. If
the archive remains selected, adopt a revised archive-consistent acceptance
rule and disclose the current-service comparison as a version difference.
The catalog's agreement checkbox was observed but not accepted.

The new [archive-route recommendation](archive_route_recommendation.md)
provides a concrete alternative to inspecting the current catalog: keep the
immutable publication-time release as the baseline, disclose Codex as a later
derivative, and adopt an explicit archive-consistent acceptance rule after
Rüzgar chooses that route. Its aggregate check is partial and does not itself
turn this gate into a pass.
