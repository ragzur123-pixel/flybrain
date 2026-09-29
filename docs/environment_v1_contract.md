# P3 virtual vehicle contract — pre-freeze v1, updated 2026-09-29

This is an **engineered 2D software environment**. Its numerical choices
are `ASSUMPTION` pilot candidates, not measurements of fly sensory or
motor physiology. The authoritative executable values are in
`configs/environment_v1.yaml` (JSON-compatible YAML 1.2). No neural
controller is connected.

## State, action, and motion

- State: center position `(x,y)` in meters, heading `θ` in radians, and
  completed-step count. The arena is 10×10 m with a 0.15 m vehicle radius.
  One fixed rectangular obstacle occupies `[4.5,5.5]×[7,8]` m. The
  goal and point light are both centered at `(8,5)` m; goal radius is
  0.35 m. This coupling is a task design choice, not a fly claim.
- Fixture reset uses position `(2,5)` m and a heading uniformly sampled from
  `[-0.3,+0.3]` rad using `Random(seed)`. Named experimental splits shift
  start and goal y by one of `-0.5, 0, +0.5` m, selected uniformly by
  `Random(seed XOR 1296127045)`. The optional `start_pose`
  argument is a software fixture override, not a controller input.
- The action is `(left_speed,right_speed)` in m/s. Each value is clipped
  to `[0,1]`; NaN/Inf is rejected. With `dt=0.1` s and wheel base
  `b=0.4` m, `v=(left+right)/2`, `ω=(right-left)/b`,
  `x_next=x+dt*v*cos(θ)`, `y_next=y+dt*v*sin(θ)`, and
  `θ_next=wrap(θ+dt*ω)`. Position uses the pre-step heading.
- A proposed move that touches a wall or obstacle ends the episode as
  `collision`; the pose remains at its last valid state. Otherwise a
  center within `goal_radius+vehicle_radius` of the goal ends as `goal`.
  The 300-step limit yields `timeout` if neither event occurred.
  Priority is collision, then goal, then timeout. An ended episode
  rejects further actions.

## Observation boundary and reward

The controller observation contains exactly `left`, `center`, `right`
unit-interval light intensities in that order. For channel offset
`φ` (`+π/4,0,-π/4`), cue bearing `β`, and squared goal distance `d²`,
the clean value is

`clip(max(0, cos(wrap(β-θ-φ)))² / (1+0.1*d²), 0, 1)`.

The observation excludes pose, goal coordinates, map, scenario, step,
and perturbation label. The `info` dictionary contains only step and
status. The separate `pose_for_logging()` and
`applied_wheel_speeds_for_logging()` and `map_for_logging()` methods are for runner records;
they must never be passed to a controller. Reward is a shared -0.001
per step, plus +1 on goal, -1 on collision, and +0 on timeout. Sensor
loss writes 0.0 with no extra missingness flag.

## Scenario contract

All scenarios use the same start/goal/map and heading seed. Separate
`Random(seed XOR 0x5eed5eed)` draws D1 noise, so D1 cannot advance the
heading stream. `onset_step=20` means sensors first change in the
observation returned after the 20th transition; D4 first changes the
21st action. Each change persists thereafter.

| Scenario | Only intended change | Pilot candidate severity |
| --- | --- | --- |
| D0 | Clean sensors and motors | None |
| D1 | Independent zero-mean Gaussian noise on the three sensed values; clip each to `[0,1]` | Standard deviation 0.08 |
| D2 | Left sensed value replaced with 0 | One channel |
| D3 | Swap sensed left and right values | One pair |
| D4 | Scale applied right motor speed after action clipping | Gain 0.5 |

The scenario severities and onset are **pre-freeze pilot candidates**.
A constant fixed-command demonstration is not a pilot or evidence of
controller quality.

## Named splits, map sampling, and dynamic cue

The four named split pools are inclusive and disjoint: `pilot=10000–10063`,
`train=20000–20063`, `validation=30000–30063`, and
`final_test=40000–40063`. The same three y-offset maps are sampled
uniformly in each pool. `reset(seed, scenario, split=...)` rejects a seed
outside that split's range. A `seed_group` is the episode seed: matched
scenarios get the same map, start, heading, goal, and cue clock. The
heading, map, and D1 noise use independent seeded streams. These are
reserved **pools**, not a decision on the final count `S` or train/test
episode budget. Training and tuning must use only `train`, `validation`,
or pilot pools as declared later; `final_test` stays held out. A fixture
reset uses the historical static map/cue and is outside all experiment
manifests. The runner must pass a named split for an experimental episode.

All named splits use the same step-clock cue schedule. Steps 0–39 show
the goal light; 40–69 show a source 3 m above the goal; 70–99 show one
3 m below it; 100–119 have no light; and step 120 onward restores the
goal light. The cue position and the switch times depend only on the
completed-step count and map offset, never on controller action or outcome.
At each step the cue uses the same bearing/attenuation formula above;
off means three clean zero readings. D1–D3 apply after this clean cue is
computed, so D1 can add noise during cue loss. The goal and reward stay
fixed through cue changes. The cue phase is absent from observation and
`info`. This sequence is a software task assumption, not fly physiology.

Before looking at controller outcomes, the pilot diagnostic will record
goal success, collision, steps and path length; mean absolute heading error
to each visible cue during each 30-step switch window; first step with
heading error at most π/6 for five consecutive observations after each
switch; and absolute heading change during the 20-step cue-loss window.
Undefined reorientation time is recorded as missing, not replaced with a
timeout success. These are **pilot task-adequacy diagnostics**, not the
main final metric. The simple-rule reference and pilot checks remain P6
work; the final primary metric and seed count remain open under ISSUE-004.

## Verification and limits

`tests/test_vehicle_env.py` checks seeded replay, clean-prefix
matching, independent D1 noise, D2 channel loss, D3 swap, D4 motor
change, mirrored headings, bounds, obstacles, goal, timeout,
non-finite action rejection, and the observation/info boundary.
`data/derived/environment_fixture_trace.json` and
`figures/environment_fixture.png` show a deterministic **fixed wheel
command** `(0.7,0.7)` from `(2,5,0)`: D0 reaches the goal in 79 steps;
D4 times out after 300. These values test software mechanics only.
`src/flyai/episode_record.py` writes the guide's complete `episodes.csv`
column set in `data/derived/environment_episodes_fixture.csv`. One
fixed-command success has `success=1, termination_reason=goal`; the
fixed-command failure has `success=0, termination_reason=timeout` and is
still a completed software episode. `shortest_valid_path` is blank
because an obstacle-aware reference path has not been validated; a
straight-line guess would misstate that metric. `wall_seconds` is an
observed runtime, so rerun checks compare the other deterministic fields.
These fixture rows are outside pilot and final manifests. The historical
fixture config is preserved exactly as
`configs/environment_fixture_2026-09-28.yaml`; its SHA-256 matches the
saved trace and `render_vehicle_fixture.py --verify-existing` still
recomputes it. The named-split dynamic cue is checked by software tests;
its ability to separate controllers remains untested until P6.
