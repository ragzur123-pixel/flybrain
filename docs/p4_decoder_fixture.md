# Exploratory rate-to-wheel interface fixture — 2026-09-29

**Status: software integration check only.** The owner has not selected a P4
model route or motor mapping. This fixed D0 run does not use pilot, training,
validation, or final-test seeds. It establishes that the current virtual
sensor, candidate unsigned rate probe, engineered decoder, and vehicle can
execute one bounded episode without a numerical failure.

## Predeclared calculation

`configs/decoder_fixture_v0.yaml` (SHA-256
`340f82f7358d7985a5d53f13eed5e51a39e880cbcf8d4c103938bbb8bdab8aa8`)
was written before the fixture ran. The graph and rate update come from
`configs/unsigned_rate_probe_v0.yaml` and the pinned publication-time 2024
FAFB v783 extraction. Four modeled outputs are ordered DNp20 left/right,
DNp22 left/right. The engineered score is

`opponent = (DNp20_L + DNp22_L - DNp20_R - DNp22_R) / 2`.

Virtual left/right wheel speeds are `clamp(0.6 - 0.5*opponent, 0, 1)` and
`clamp(0.6 + 0.5*opponent, 0, 1)` m/s. Positive score turns the virtual
vehicle left by definition. Equal family weighting, base speed, gain, and
clipping are **ASSUMPTION**, not biological measurements. The controller
receives only the environment's three intensity values; pose is read only
for the saved trace. The run uses D0, `split=fixture`, seed 1 and exact start
pose `(2,5,0)`; every controller state resets at the start.

## Observed software output

The saved trace is `data/derived/decoder_fixture_v0.json` (SHA-256
`f55f44a4934a8d179b3dd159c6d5fad19e72ccf50d21105aa59da0e372e1e132`).
The fixture reached the virtual goal at step 93; final pose was approximately
`(7.574, 5.150, -0.105)`. This one deterministic fixture is not evidence of
general controller performance or perturbation recovery.

The same decoder applied to each earlier 12-step, unit-intensity synthetic
cue trace gives opponent scores `+0.191343` for left, `+0.082815` for center,
and `-0.274159` for right. Thus the candidate does turn in opposite directions
for side cues, but a center-only cue also requests a left turn. The center
bias follows from the *specific assumed normalization and readout*; it is a
software finding, not a statement about observed fly neurons. It prevents
adopting this uncorrected mapping as a neutral-center P4 controller without
further model choice and tests.

The [preview](../figures/decoder_fixture_v0.png) combines the fixture path
and the three synthetic cue scores. Its SVG generator is
`src/flyai/render_decoder_fixture.py`; the PNG is a raster copy. Neither
the goal outcome nor the side-cue scores validate a biological motor sign.

## Verification and next decision

- `tests/test_decoder_fixture.py` passed three tests (exit 0): mirrored
  synthetic readout, silence, clipping, invalid inputs, output order, replay,
  finite state, wheel bounds, and observation schema.
- The full unittest suite passed 50 tests (exit 0) on 2026-09-29.
- `render_decoder_fixture.py --verify-existing` checks the saved trace and
  SVG byte for byte against recomputation and checks that the unit-cue source
  trace still matches its pinned graph/config.
- The P4 model route, justified sign/weight policy, neutral-center mapping,
  learning permissions, and dynamic-cue verification remain open. No pilot
  or final outcome has been generated.
