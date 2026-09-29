# C03 archive path feasibility — 2026-09-28

Status: **anatomical reachability screen complete; no C04 circuit
selection, motor decoder, or behavioral run**. This follows the
[predeclared C03 rule](path_feasibility_rule.md).

Raw connection SHA-256: `24f960ae3e7d4f8cd30db3b62e99fb5179cc3d1e76d8c155bfb441e9737d3faf`.
C02 inventory SHA-256: `1c77dfa444aae145820b3c3b9cb18efa1286e52ef907bce3737e540cc8a30229`.
Rule SHA-256: `a7b334701d2a99a4c6170d09a98e3fb3724f95b55861f647ee50866ed0677c45`.
Graph rows rescanned: **16,847,997**; directed candidate pairs: **958**.
The new pair list agreed exactly with the earlier exploratory screen.
Counts are unique photoreceptor IDs, not synapses or distinct paths.

| Pair minimum | Output | Route | Photo inputs L/R/C | All unique | Fully same-side | Status |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| 5 | DNp22 left | via_OCG01 | 8/35/11 | 54 | 8 | (blank) |
| 5 | DNp28 left | direct | 18/0/0 | 18 | 18 | (blank) |
| 5 | DNp20 left | via_OCG01 | 7/28/18 | 53 | 7 | (blank) |
| 5 | DNp22 right | via_OCG01 | 33/29/16 | 78 | 29 | (blank) |
| 5 | DNp28 right | direct | 0/31/0 | 31 | 31 | outlier_seg |
| 5 | DNp20 right | via_OCG01 | 20/31/13 | 64 | 31 | (blank) |
| 1 | DNp22 left | via_OCG01 | 62/73/47 | 182 | 62 | (blank) |
| 1 | DNp28 left | direct | 71/0/0 | 71 | 71 | (blank) |
| 1 | DNp20 left | via_OCG01 | 62/47/47 | 156 | 62 | (blank) |
| 1 | DNp22 right | via_OCG01 | 75/68/59 | 202 | 68 | (blank) |
| 1 | DNp28 right | direct | 0/71/0 | 71 | 71 | outlier_seg |
| 1 | DNp20 right | via_OCG01 | 75/68/59 | 202 | 68 | (blank) |

At both thresholds, every output role passes the declared
left/right **reachability-only** screen. DNp28 right remains
`outlier_seg`; C04 must decide whether to include it. The OCG01
routes retain mixed-side and center inputs in their all-side totals.
A threshold of five is an analytical convention, not biological
proof that smaller archive connections are irrelevant. Neither
reachability nor the 3D mesh establishes steering sign or an
appropriate virtual vehicle motor mapping.
