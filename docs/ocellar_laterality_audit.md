# Exploratory ocellar laterality audit

This recount uses the saved publication-time v783 candidate-pair screen; it
does **not** independently rescan the raw graph or resolve the current Codex
count mismatch. No circuit, synapse threshold, or motor decoder is selected.
Input JSON SHA-256: `3664c471f140c718ab72e2e9c472c7b871b6ff22ffc886b1da5084a0937ea7dd`. Pair-summed exploratory threshold: `5`.
Counts are unique annotated photoreceptor or OCG01 root IDs, not synapses.
Visual preview: `figures/ocellar_laterality.png`.

| Output | Direct photos L/R/C | OCG inputs L/R/C | Two-hop photos L/R/C | All two-hop photos | Fully same-side two-hop photos |
| --- | ---: | ---: | ---: | ---: | ---: |
| DNp22 left | 0/0/0 | 2/2/0 | 8/35/11 | 54 | 8 |
| DNp28 left | 18/0/0 | 0/0/0 | 0/0/0 | 0 | 0 |
| DNp20 left | 0/0/0 | 3/1/0 | 7/28/18 | 53 | 7 |
| DNp22 right | 0/0/0 | 2/3/0 | 33/29/16 | 78 | 29 |
| DNp28 right | 0/31/0 | 0/0/0 | 0/0/0 | 0 | 0 |
| DNp20 right | 0/0/0 | 1/4/0 | 20/31/13 | 64 | 31 |

L/R/C means biological left/right/center annotation, not image x coordinate.
A fully same-side chain has both the photoreceptor and OCG01 on the
output's annotated side. A photoreceptor can reach an output through
more than one OCG01, so side counts describe unique photoreceptor IDs
rather than distinct paths. Contralateral and center inputs are retained
in the all-side counts; they cannot be interpreted as an ipsilateral
sensor channel. Revisit the input encoding and output decoder before
calling this a left/right steering circuit. Anatomical side does not
establish excitation sign or a turning direction.
