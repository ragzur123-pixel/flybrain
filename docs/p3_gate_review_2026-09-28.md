# P3 environment gate review — 2026-09-28

**Result: PARTIAL.** The independent virtual vehicle's core mechanics
and D0–D4 software perturbations are specified, implemented, and tested.
The guide's P3 gate also requires a time-varying task specification and
test-split policy before a pilot or neural controller result; those
remain open. The episode logging schema is now implemented for fixtures.

| Check | Result | Evidence |
| --- | --- | --- |
| P2 prerequisite | PASS | `docs/p2_gate_review_2026-09-28.md` applies the guide's anatomical P2 criteria; the P4 sign/mapping questions remain separate. |
| Units, state, motion, bounds, obstacle, goal | PASS as pre-freeze software contract | `configs/environment_v1.yaml`; `docs/environment_v1_contract.md`; `src/flyai/vehicle_env.py`; focused collision/action/goal/timeout tests. Numerical values are pilot-candidate assumptions. |
| Sensor boundary and D0–D4 isolation | PASS for current contract | Three unit-interval light channels and step/status only in `info`; six new tests cover replay, clean-prefix matching, D1 deterministic noise, D2/D3 sensor changes, D4 motor change, mirroring and invalid actions. |
| Reproducible visual fixture | PASS, software only | `render_vehicle_fixture.py --verify-existing` recomputes trace and SVG exactly; config hash matches; fixed action D0 goal at 79 steps, D4 timeout at 300. PNG was visually inspected. |
| Episode record | PASS for fixture schema | `src/flyai/episode_record.py` writes all 13 guide fields to `data/derived/environment_episodes_fixture.csv`; one success and one completed timeout failure were checked by two tests. `shortest_valid_path` remains blank pending an obstacle-aware method. |
| Split policy | OPEN | Train/validation/held-out seed lists and map distributions are not defined. Fixture rows are labeled `split=fixture` and excluded from experiments. |
| Dynamic cue and pilot task adequacy | OPEN | Current point light is fixed. A time-varying cue and the simple-rule diagnostic must be specified and checked with pilot-only seeds (`docs/control_design_note.md`). |

The fixture has **no neural model, photoreceptor encoder, DNp20/DNp22
decoder, adaptation, or experiment score**. Finish the open dynamic-cue
and split-policy contract parts, then repeat the P3 gate review before
P4 integration.
