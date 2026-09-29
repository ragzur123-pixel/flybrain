# C04 candidate option footprint — 2026-09-28

**Anatomical comparison only.** This report does not select a circuit,
cap, input encoder, output decoder, or motor sign. It filters the
C03-verified candidate ordered-pair list; it does not rescan the raw
graph independently. Each edge meets the stated pair-summed minimum,
and every retained edge lies on at least one complete role-correct
input-to-output path. `strict_same_side` is a hypothetical reduction
that drops other-side and center paths, not a claim about physiology.

Raw graph SHA-256: `24f960ae3e7d4f8cd30db3b62e99fb5179cc3d1e76d8c155bfb441e9737d3faf`.
Saved candidate-pair screen SHA-256: `3664c471f140c718ab72e2e9c472c7b871b6ff22ffc886b1da5084a0937ea7dd`.
C02 inventory SHA-256: `1c77dfa444aae145820b3c3b9cb18efa1286e52ef907bce3737e540cc8a30229`.

| Pair minimum | Option | Side policy | Nodes | Directed edges | Pair-summed synapses | Photo / OCG / outputs | Every output reachable |
| ---: | --- | --- | ---: | ---: | ---: | --- | --- |
| 5 | ocg_family | all_sides | 119 | 169 | 4434 | 103 / 12 / 4 | yes |
| 5 | ocg_family | strict_same_side | 53 | 62 | 2321 | 42 / 7 / 4 | yes |
| 5 | dnp20_pair | all_sides | 97 | 105 | 2128 | 87 / 8 / 2 | yes |
| 5 | dnp20_pair | strict_same_side | 45 | 50 | 1057 | 38 / 5 / 2 | yes |
| 5 | dnp22_pair | all_sides | 98 | 124 | 2828 | 88 / 8 / 2 | yes |
| 5 | dnp22_pair | strict_same_side | 44 | 52 | 1602 | 37 / 5 / 2 | yes |
| 5 | dnp28_direct | all_sides | 51 | 49 | 464 | 49 / 0 / 2 | yes |
| 5 | dnp28_direct | strict_same_side | 51 | 49 | 464 | 49 / 0 / 2 | yes |
| 1 | ocg_family | all_sides | 240 | 500 | 5086 | 224 / 12 / 4 | yes |
| 1 | ocg_family | strict_same_side | 141 | 217 | 2609 | 130 / 7 / 4 | yes |
| 1 | dnp20_pair | all_sides | 227 | 450 | 3085 | 214 / 11 / 2 | yes |
| 1 | dnp20_pair | strict_same_side | 139 | 210 | 1399 | 130 / 7 / 2 | yes |
| 1 | dnp22_pair | all_sides | 238 | 488 | 3786 | 224 / 12 / 2 | yes |
| 1 | dnp22_pair | strict_same_side | 139 | 210 | 1916 | 130 / 7 / 2 | yes |
| 1 | dnp28_direct | all_sides | 144 | 142 | 651 | 142 / 0 / 2 | yes |
| 1 | dnp28_direct | strict_same_side | 144 | 142 | 651 | 142 / 0 / 2 | yes |

These counts describe the induced role-path graph, not the full
connectome or a final reduced network. Pair-summed synapses count
each retained directed edge once, even if it serves multiple paths.
A strict same-side graph may discard real cross-side/center anatomy.
Right DNp28 retains its `outlier_seg` annotation in the machine-readable
output. Blank status on other candidates is not quality assurance.
No option is ranked by simulated performance or chosen here.
