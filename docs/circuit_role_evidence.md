# C01 candidate role evidence — 2026-09-28

Status: **C01 class-level evidence complete for the selected 2024 archive;
C02 all-candidate ID provenance is in `docs/candidate_id_inventory.md`;
Rüzgar selected the DNp20+DNp22 family for C04 anatomical extraction.**
P2 model-weight and virtual mapping rules remain open. These annotations
are not a verified motor circuit.

The biological route is described in Dorkenwald et al. 2024, “Ocellar circuit,
from inputs to outputs” and Fig. 7/Extended Data Fig. 10 (FW-039, FW-050).
Schlegel et al.'s v2.1.0 annotation supplement defines the snapshot-specific
fields and cautions for `outlier_seg` (FW-048–FW-049). The local values below
were recounted from the checksum-pinned annotation TSV and proofread-root
array after P1 passed (FW-063).

| Candidate class | Role supported by paper | v2.1.0 field and local count | Biological side labels | Limits before a vehicle mapping |
| --- | --- | --- | --- | --- |
| Ocellar retinula cell | Light-sensing ocellar input class | `cell_type=ocellar retinula cell`; 273 IDs | left 100, right 97, center 76 | An artificial left/right cue is a model input; the paper does not supply a vehicle sensor encoder. Center cells cannot silently be assigned to a side. |
| OCG01 | Ocellar projection interneurons on a route to downstream descending cells | `cell_type` starts `OCG01`; 12 IDs | left 6, right 6 | Paths mix biological sides in the local graph at the exploratory threshold (FW-061); no functional sign follows from an edge count. |
| DNp20 / DNOVS1 | Descending output candidate receiving strong OCG01 input | `hemibrain_type=DNp20`; 2 IDs | one per side | A descending neuron is not a body motor neuron or a verified left/right wheel command. |
| DNp22 / DNOVS2 | Descending output candidate receiving strong OCG01 input | `cell_type=DNp22`; 2 IDs | one per side | Its two-hop input population includes opposite-side and center photoreceptors (FW-061). |
| DNp28 | Direct ocellar-ganglion descending output candidate | `hemibrain_type=DNp28`; 2 IDs | one per side | The right ID `720575940640142141` has `status=outlier_seg`. Direct input laterality is anatomically clean at exploratory threshold five, but motor sign and segmentation suitability are unverified. |

The class parser found **291 unique candidate root IDs**; all 291 occur in
the pinned proofread-root array. All class rows except the right DNp28 have
a blank `status` field. A blank status is not functional validation.
The local `side` field is the released biological-side label, despite the
imaging-axis inversion documented by Schlegel et al.; camera x position is
not a substitute for this label (FW-049).

## C04 handoff after C02/C03

1. The complete [candidate-ID inventory](candidate_id_inventory.md) and
   machine-readable CSV cover all 291 IDs; the earlier 19-ID packet matches
   on role, side, and status. Do not select IDs because they later improve
   vehicle scores.
2. The [predeclared C03 rule](path_feasibility_rule.md) and
   [fresh archive screen](path_feasibility_v1.md) confirm bilateral
   reachability at pair minimums five and one. These analytical screens
   leave right DNp28's segmentation flag and mixed-side OCG01 paths open
   for the [C04 decision packet](c04_circuit_decision_packet.md).
3. The [selected all-side subnetwork](selected_subnetwork.md) was extracted
   before behavior data. Decide the virtual sensor encoding and motor decoder
   as model assumptions; do not infer wheel direction from an annotated side.

The [3D Neuroglancer preview](visual_previews.md) shows the left/right DNp28
meshes, while the [side-resolved chart](../figures/ocellar_laterality.png)
shows archive graph counts. Neither establishes a completed controller.
