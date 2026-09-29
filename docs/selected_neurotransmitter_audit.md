# Selected v783 neurotransmitter audit — 2026-09-28

**Observation, not a sign assignment.** The pinned v2.1.0 annotation
provides `top_nt` predictions and average `top_nt_conf` for all
119 selected neurons, but no `known_nt` value for any of them.
A prediction is not a confirmed transmitter or postsynaptic effect.

| Predicted top transmitter | Selected neurons | Outgoing selected edges | Pair-summed synapses on those edges |
| --- | ---: | ---: | ---: |
| acetylcholine | 21 | 33 | 1526 |
| glutamate | 11 | 13 | 1874 |
| serotonin | 87 | 123 | 1034 |

`top_nt_conf` min/median/max: 0.357 / 0.594 / 0.863.
The full per-ID predictions, confidence, and
source provenance are in `data/derived/selected_neurotransmitter_audit.csv`.
This set has 87 serotonin-predicted neurons and no confirmed
transmitter values. Those neurons supply 123/169 selected outgoing
edges. Eckstein et al. report serotonin as their least reliable
prediction and document sensory-neuron mispredictions (FW-070).
The classifier predicts six transmitters and does not include
histamine. Neither the annotation nor Shiu et al.'s simplified
model verifies the identity or effect of these selected v783
ocellar synapses. Any sign policy must be labeled as a model
assumption, including for glutamate and serotonin.

Pinned annotation SHA-256: `30be6c73975a70c56d930e27911f36455d3886e15abf383b78edd2a5d679e0b6`.
Selected node CSV SHA-256: `3fe59923fb1afcbd0ce47773d05f63fa59a0cc63433c72aab756ac631f4461d2`.
Audit CSV SHA-256: `b55a0114a400dcdeea9374da8c348a73fd2eb7f2c26e5de5a96b899ddd18b0d3`.
