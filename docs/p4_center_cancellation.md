# Exploratory center-channel cancellation — 2026-09-29

**Status: software decoder candidate only.** Rüzgar has selected the
publication-time 2024 FAFB v783 archive and the DNp20+DNp22 anatomical
output family, but has not selected a P4 neural model or virtual motor
mapping. This note compares two deterministic software fixtures, not pilot
or final experiment results.

## Declared v1 calculation

The pre-run `configs/decoder_fixture_v1.yaml` has SHA-256
`a26337b87081f875afd7cdd9ce72ccec79fe288d8a76e63b440d7f93026459b6`.
It retains v0's
0.6 m/s base speed, 0.5 m/s gain, and [0,1] m/s wheel bounds. At every
step, the same zero-initialized unsigned rate probe runs twice:

1. The full probe receives the observed virtual left, center, and right
   intensities.
2. A reference copy receives `(left=0, center=observed center, right=0)`.
3. The virtual turn score is the full left-minus-right opponent score minus
   the reference opponent score. Wheel speeds use the same v0 formula with
   this corrected score.

The extra probe uses only the allowed three-channel observation. Pose,
goal, map, reward, and scenario are unavailable to the decoder. The two
probes reset together. This subtraction is an **engineered readout for a
linear software model**, not evidence of an inhibitory cell or fly motor
sign. It discards center-channel influence on turning by construction;
whether that is desirable for the research task remains open. The reference
copy also changes memory and compute cost, which must be applied consistently
to comparison topologies if the design is selected.

## Software checks and observed outputs

The derived comparison is `data/derived/decoder_fixture_v1.json` (SHA-256
`3d10b1303d2c106e12105f98da300f59dd002d15cbea961dc4c3485ce11ab501`).
It verifies the historical v0 fixture against recomputation before saving
the v1 fixture. Unit-intensity left, center, and right cues ran for 12 steps
each, resetting between cues:

| Cue | Raw opponent score | Center reference | Corrected score |
| --- | ---: | ---: | ---: |
| left | +0.191343 | 0 | +0.191343 |
| center | +0.082815 | +0.082815 | 0 |
| right | −0.274159 | 0 | −0.274159 |

A changing center-only stream had zero residual through onset, level
changes, and loss. In a left-to-right-to-off side-cue sequence, adding a
changing center stream changed the corrected score by at most
`1.11e-16` in this calculation. These are floating-point software checks
of the current linear probe. They do not establish mirror equality: the
left and right score magnitudes still differ.

The same fixed D0 fixture, seed 1 and start pose `(2,5,0)` reached the
virtual goal at step 93 under both v0 and v1. The v1 final pose was about
`(7.574, 4.845, +0.104)`; v0 ended near `(7.574, 5.150, −0.105)`.
The [comparison preview](../figures/decoder_fixture_v1.png) shows these
two paths and the synthetic score change. This one easy, static fixture
does not establish moving-cue control, perturbation recovery, robust
performance, or an adopted P4 model.

## Verification and remaining choice

- `tests/test_center_cancelled_decoder.py` passed five tests (exit 0) for
  center neutrality under changing input, side-cue invariance, switch and
  cue loss, reset, invalid input/config, wheel bounds, and deterministic replay.
- The full unittest suite passed 55 tests (exit 0) on 2026-09-29.
- `render_center_cancelled_fixture.py --verify-existing` recomputes the
  historical and current fixtures and checks the v1 JSON/SVG bytes.
- P4 remains open: select a numerical model, decide whether center
  cancellation and unequal side gains are acceptable, specify learning
  and fair-control interfaces, and verify dynamic-cue behavior before a
  pilot or gate review.
