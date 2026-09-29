# C04 circuit selection packet — prepared 2026-09-28

**Status: historical review packet.** Rüzgar subsequently selected option 1,
the DNp20+DNp22 family, for anatomical extraction. The selected rule is in
[`configs/subnetwork_selection.yaml`](../configs/subnetwork_selection.yaml),
and the [C05 extraction](selected_subnetwork.md) retains all qualifying
left/right/center paths. The packet below records the options as presented.
The selected data source
is the publication-time 2024 FAFB v783 archive and annotation tag `v2.1.0`.
The [C02 inventory](candidate_id_inventory.md) verifies all 291 candidate
IDs. The [predeclared C03 screen](path_feasibility_v1.md) checks directed
anatomical reachability at pair-summed minima five and one (FW-065). No
vehicle scores, motor decoder, or pilot results informed this packet.

## Candidate output pairs

| Route | Left output root ID | Right output root ID | Fully same-side photo IDs at minimum five, L/R | Main selection limit |
| --- | --- | --- | ---: | --- |
| Photoreceptor → OCG01 → DNp20 | `720575940629390123` | `720575940644166048` | 7 / 31 | Other-side and center inputs also reach these outputs; a same-side-only extraction would be a declared simplification. |
| Photoreceptor → OCG01 → DNp22 | `720575940615043368` | `720575940631225996` | 8 / 29 | Same mixed-side issue; these counts alone do not rank DNp22 above DNp20. |
| Photoreceptor → DNp28 | `720575940621561697` | `720575940640142141` | 18 / 31 | Right output has released `outlier_seg` status; bilateral path counts do not clear that flag. |

These are the six output annotations from the selected inventory, not a
chosen subnetwork. The 12 OCG01 candidates and 273 photoreceptors still
need a deterministic, auditable inclusion rule. All numbers count unique
photoreceptor IDs, not synapse totals, signs, or distinct paths.

## Reviewable options

1. **OCG01-mediated DNp20/DNp22 family.** Retain the four unflagged
   descending-output IDs as candidate readouts and choose a reproducible
   rule for OCG01 and photoreceptor inclusion. This preserves both
   source-described OCG01 recipient classes and avoids using the flagged
   DNp28 as a necessary bilateral output. It needs an explicit policy for
   cross-side and center input and a four-output-to-two-action decoder.
2. **Direct DNp28 pair.** The direct archive paths are side-specific in the
   C03 screen and use fewer intermediate roles. Its right output is flagged
   `outlier_seg`; choosing it requires an evidence-based segmentation
   review and a stated treatment if the right cell proves unsuitable.
3. **One unflagged OCG01-mediated pair.** DNp20 or DNp22 alone minimizes
   the number of outputs for a first controller. Neither pair has a
   demonstrated functional advantage; choosing between them needs a
   predeclared anatomical/resource comparison, not later vehicle scores.

**Recommended next review:** start with option 1 as the structural candidate
because both paired classes have archive provenance and blank status fields,
while preserving DNp28 as a separately reported direct-path comparison.
This is an engineering recommendation under uncertainty, not a claim of
biological superiority. A blank status is not proof of complete segmentation.
Rüzgar's choice was recorded in `docs/decisions.md` before the selected
configuration and extraction were run.

## Questions the selected configuration must answer

- Which output pair(s) and exact input/intermediate roles are included?
  If multiple output pairs are kept, how are they combined without using
  final behavior scores to choose the decoder?
- Do all directed archive connections among chosen roles enter the
  subnetwork, or only fully same-side paths? What happens to center and
  opposite-side photoreceptors? A same-side restriction changes the graph
  and must be stated as a model reduction, not a biological observation.
- Is the pair-summed minimum five retained for selection? Specify whether
  threshold one is sensitivity only. Record the graph hash, ordered-pair
  aggregation, and treatment of multiple neuropil rows.
- What are maximum nodes and directed edges within the local resource cap?
  Specify deterministic ranking, tie-breaks, and what happens if a cap
  removes the only input-to-output path for a side.
- Is right DNp28 excluded, included after segmentation review, or retained
  only for sensitivity analysis? Never silently pair it with an unflagged
  neuron as an interchangeable equivalent.
- Which artificial cue is encoded into left, right, and any center input?
  How are descending outputs mapped to virtual left/right action? These
  mappings and any motor sign are model assumptions to define in P3/P4,
  not anatomical facts inferred from side labels.

## Acceptance before C05 extraction

Record the owner choice and rejected alternatives in `docs/decisions.md`.
Write the exact IDs/classes, ordered direction, threshold, side policy,
size bounds, path preservation, and tie-breaks in
`configs/subnetwork_selection.yaml` before behavior evaluation. Then
extract only from checksum-verified raw inputs; record before/after
nodes, edges, synapse totals, role counts, graph hash, and bilateral
reachability. Test directionality and tie-breaking on a synthetic graph
and audit a few selected real edges against the archive. This packet
alone does not pass P2.
