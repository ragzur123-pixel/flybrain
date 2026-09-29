# Selected edge raw-row audit — 2026-09-28

Seven reproducibly chosen edges were checked against a fresh scan
of the same checksum-pinned 16,847,997-row raw archive. For each
edge, the neuropil-row count and summed `syn_count` agreed with
the selected edge CSV. Reverse directions were counted separately.
This is a raw-file audit, not a current Codex portal comparison or
physiological validation.

| Pre role/side → post role/side | Pre ID → post ID | Raw synapses | Raw neuropil rows | Reverse synapses |
| --- | --- | ---: | ---: | ---: |
| OCG01 left → DNp20 left | `720575940621202670` → `720575940629390123` | 242 | 2 | 10 |
| OCG01 right → DNp20 right | `720575940631187287` → `720575940644166048` | 240 | 2 | 18 |
| OCG01 left → DNp22 left | `720575940629102891` → `720575940615043368` | 417 | 2 | 2 |
| OCG01 right → DNp22 right | `720575940615097490` → `720575940631225996` | 314 | 2 | 1 |
| photoreceptor center → OCG01 left | `720575940607293570` → `720575940621202670` | 16 | 1 | 0 |
| photoreceptor left → OCG01 left | `720575940630424631` → `720575940627972485` | 37 | 1 | 0 |
| photoreceptor right → OCG01 right | `720575940640123299` → `720575940630751031` | 26 | 1 | 0 |

Raw graph SHA-256: `24f960ae3e7d4f8cd30db3b62e99fb5179cc3d1e76d8c155bfb441e9737d3faf`.
Selected edge CSV SHA-256: `d69d81db5cbcfdc4300d054853df455fdbfcf2985d87c1e375cafba26ba0b2a4`.
The machine-readable JSON records each matched neuropil row.
