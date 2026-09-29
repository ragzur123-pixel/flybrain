# Circuit candidate history and selected route

Date: 2026-09-25, reviewed 2026-09-28. Rüzgar delegated the framing choice; visual orientation stabilization is chosen in `docs/decisions.md`. This table records the historical candidate screen. Rüzgar later selected the DNp20+DNp22 family, and its [119-node anatomical extraction](selected_subnetwork.md) is now available (FW-067). Ten current Codex pair counts differ from the selected publication-time archive (`docs/codex_reconciliation.md`). Motor signs, virtual mappings, and behavior outcomes remain unvalidated.

| Candidate | Primary source support | Fit to 2D vehicle question | Main risk / validation |
| --- | --- | --- | --- |
| Ocellar photoreceptors → DNp28 directly, and photoreceptors → OCG01 → DNp20/DNOVS1 or DNp22/DNOVS2 | Dorkenwald et al. distinguish the direct ocellar-ganglion DNp28 route from strong OCG01 input to DNp20/DNp22 (FW-039, FW-050). The revised local screen observes both route types (FW-051); a side-resolved recount shows that DNp20/DNp22 two-hop totals mix both sides and center (FW-061). | Left/right visual channels and descending outputs could support a deliberately simplified orientation-control analogy, but only after the mixed-side routes are explicitly encoded. | The documented circuit concerns light sensing, gaze stabilization, and flight/head control. Mapping its outputs to left/right vehicle motors is a **model assumption**, not a measured turn command. Right DNp28 has an `outlier_seg` flag. Manual edge checks and a frozen threshold remain. |
| Shiu et al. antennal-grooming sensory pathway | Published computational model tests Johnston's-organ sensory input through antennal-grooming intermediates (FW-025–FW-027). | Useful as a neural-dynamics and validation reference. | The original model uses v630 and the behavior is grooming, with no natural link to vehicle heading or obstacle avoidance. Any v783 translation needs fresh class/ID/path evidence. |

**Chosen framing and structural route:** the planned vehicle task is visual orientation stabilization under D0–D4 perturbations. The predeclared C03 scan distinguished direct photoreceptor→DNp28 from OCG01-mediated DNp20/DNp22 routes (`docs/path_feasibility_v1.md`; FW-065). Rüzgar selected the latter family; the C04 rule and C05 extraction retain all qualifying left/right/center archive paths at threshold five. This does not establish that the biological circuit controls a vehicle or approve a decoder. The 2D task must make artificial visual input and left/right output mappings explicit. Obstacles can be environmental challenges only if their sensing is separately declared; obstacle avoidance is not the claimed biological function.

The [side-resolved audit](ocellar_laterality_audit.md) (FW-061) shows why the
earlier two-hop totals cannot be called same-side sensor pathways. At the
exploratory five-synapse threshold, only 7/53 left DNp20 and 8/54 left DNp22
two-hop photoreceptor IDs form fully left-sided chains; opposite-side and
center inputs contribute to the remaining unique-ID totals. Direct DNp28
inputs are side-specific in this archive screen, but the right output's
`outlier_seg` flag remains. Neither pattern proves a steering sign.

## Historical C04 evidence checklist

1. Inspect the `v2.1.0` annotation TSV's actual schema and rows for ocellar photoreceptors, OCG01, DNp28, DNp20/DNOVS1, and DNp22/DNOVS2; record root ID, side, class/type, status, and source revision for every candidate. Do not import IDs from v630 or main-branch annotations.
2. Join only verified v783 IDs to the Zenodo proofread-root array and connection table. Check source/target direction and directed paths at a predeclared threshold; document whether multiple neuropil rows are summed.
3. Review left/right symmetry, segmentation/outlier flags, and synapse coverage, including the optic-lobe annotation limits noted by Schlegel et al. (FW-040).
4. Decide which actual sensor features feed which biological input classes, and which model outputs control left/right vehicle action. Mark the mappings as assumptions and assess whether D1–D4 perturbations still test the stated question.

Do not use preliminary vehicle scores to choose the circuit. If the anatomical path fails validation, return to the literature screen before changing the selection rule.
