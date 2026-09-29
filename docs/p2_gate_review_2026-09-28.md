# P2 circuit gate review — 2026-09-28

**Result: PASS under the project guide's P2 gate.** The owner-selected
DNp20+DNp22 anatomical extraction passes provenance, directed-path,
size, raw-edge, and reproducibility checks. The guide assigns synapse
sign/weight conversion and virtual sensor/motor mapping to P4, so those
remain open model tasks and are not conditions for starting P3. No
environment or behavioral run existed at this gate review.

| Check | Result | Evidence |
| --- | --- | --- |
| One coherent archive lineage | PASS | Selected 2024 FAFB v783 four-product manifest and archive-specific P1 gate; current Codex kept separate. |
| Candidate ID provenance and owner choice | PASS | 291-ID C02 inventory (FW-064); Rüzgar's DNp20+DNp22 choice in `docs/decisions.md`; four exact output IDs in `configs/subnetwork_selection.yaml`. |
| Directed route and side reporting | PASS for anatomy | C03 rule and fresh screen (FW-065); all-side C04 selection and selected graph (FW-066–FW-067). All four outputs have a fully same-side path, while cross-side/center paths remain in the selected graph. |
| Resource cap and graph statistics | PASS | 119 nodes ≤128, 169 directed edges ≤200; 4,434 pair-summed synapses, one 119-node weak component, zero nodes lacking an output path. Before role-path filtering: 291 candidate nodes, 958 directed pairs, 7,259 pair-summed synapses. |
| Raw-edge audit and reproducibility | PASS | Seven selected directed edges matched raw neuropil rows (FW-068). `extract_selected_subnetwork.py --verify-existing` rescanned the raw graph, matched every saved node/edge CSV row and both SHA-256 hashes. |
| Transmitter-prediction audit | PASS for data, not physiology | Exact 119-ID join to the pinned annotation: 87 serotonin, 21 acetylcholine, 11 glutamate predictions; no nonblank `known_nt` (`docs/selected_neurotransmitter_audit.md`; FW-069–FW-071). The classifier authors warn about sensory serotonin mispredictions. |
| Model weight/sign and virtual mapping | DEFERRED TO P4 | `configs/subnetwork_selection.yaml` preserves anatomical `pair_synapses` without sign, physiological strength, virtual sensor encoding, or motor decoding. `docs/p2_model_route_packet.md` lays out routes and checks; none is selected or tested. This does not block the independent P3 environment. |

The selected graph is a defensible **anatomical candidate** for the
preplanned orientation-control experiment. Its presence does not prove
that a simulated neural circuit will be stable or perform the task.
Proceed to P3 for a deterministic environment. Before P4 integration,
select and test model equations, synapse conversion, photoreceptor input
encoding, and the four-output decoder. This correction follows the P2/P3/P4
division in `FlyAI_MASTER_TODO_AND_AGENT_RULES.md`, phase-gate table.
