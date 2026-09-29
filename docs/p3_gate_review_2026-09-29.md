# P3 environment gate review — 2026-09-29

**Result: PASS for the pre-freeze software environment contract.** This
does not validate a neural controller, physiological mapping, simple-rule
comparison, or pilot task adequacy. The numerical choices remain
assumption candidates for P6.

| Gate check | Result | Evidence |
| --- | --- | --- |
| State, motion, collision, goal, timeout, reward | PASS | `configs/environment_v1.yaml`, `src/flyai/vehicle_env.py`, `tests/test_vehicle_env.py` |
| Observation boundary and D0–D4 isolation | PASS | Three light values only; `info` has step/status only. The focused and full software tests cover replay, common clean prefix, noise, loss, swap, motor gain, and invalid actions. |
| Dynamic orientation cue | PASS as software contract | Step-clock goal→upper→lower→off→goal sequence in the config; `test_dynamic_cue_switch_loss_and_restore_follow_step_clock` checks direction, loss, restoration, and no cue-phase field in `info`. |
| Seed and map split policy | PASS as software contract | Four disjoint inclusive seed pools and a shared three-offset map distribution; `reset(..., split=...)` rejects cross-split seeds. Repeated same-seed resets have equal maps/pose across scenarios. Final `S` remains unset. |
| Episode record | PASS for historical fixture | `src/flyai/episode_record.py` and its tests preserve the 13-field row with successful and failed completed episodes. Pilot/final manifests are not created. |
| Fixed-command fixture preservation | PASS | `configs/environment_fixture_2026-09-28.yaml` has the exact SHA-256 stored in `data/derived/environment_fixture_trace.json`; `render_vehicle_fixture.py --verify-existing` recomputes its trace and SVG. The historical output is not overwritten. |

The current code has no neural update, virtual photoreceptor input map,
DNp20/DNp22 motor decoder, learning, or simple-rule pilot result. The
next gate is P4 numerical/interface modeling. P6 must still use pilot-only
seeds to check D0 stability and whether the dynamic task distinguishes
the simple rule from candidate neural controllers. Final-test seeds are
reserved for post-freeze evaluation only.

## Verification commands

- `.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -v`: exit 0; 38 tests passed after the reset-state and split-validation additions.
- `.venv\Scripts\python.exe src\flyai\render_vehicle_fixture.py --workspace . --verify-existing`: exit 0; `D0 goal 79`, `D4 timeout 300`, existing trace and SVG matched.
