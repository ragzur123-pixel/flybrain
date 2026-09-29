# Exploratory moving-cue software smoke — 2026-09-29

**Status: P4 candidate integration check, not a pilot.** This check used
the publication-time 2024 FAFB v783 selected graph, the unsigned software
probe, and the center-cancelled virtual wheel decoder. No numerical neural
model or motor mapping has been adopted for the project. It must not be
reported as fly behavior, perturbation recovery, or a final comparison.

## Predeclared scope

`configs/dynamic_smoke_v0.yaml` was saved before execution (SHA-256
`543e1318d730d7696c1c7e68269e67f9944926ffe0fbb11e2853f38fc35b7594`).
It fixes `split=train`, seed 20000, paired D0 and D4, the environment's
default seeded start and map, and the v1 decoder without any parameter
update. This training-pool seed is now exposed for exploratory work; do
not treat it as independent evidence later. No pilot, validation, or
final-test seed was used. The run was bounded by the environment's
300-step limit and retained both outcomes.

The environment's declared cue clock shows goal at steps 0–39, upper cue
at 40–69, lower cue at 70–99, no cue at 100–119, and the restored goal
cue from 120 onward. The cue label, map, pose, and applied wheel speeds
are logger-only metadata. At each step, the decoder receives only the
three virtual intensity values and resets its two probe states between
scenarios.

## Observed software output

The saved [trace](../data/derived/dynamic_smoke_v0.json) has SHA-256
`8aaff7f5f8012523a1eac7879c00bf147afc27f9d0de6b7b1e45f42cbe0a8609`.
The paired runs used the same zero-offset map and goal `(8,5)`:

| Scenario | Termination | Step | Cue windows observed |
| --- | --- | ---: | --- |
| D0 | Collision | 133 | Initial goal, upper, lower, off, restored goal |
| D4 | Timeout | 300 | Initial goal, upper, lower, off, restored goal |

The D0 trace's sampled minimum center-to-goal distance was approximately
0.563 m; the environment's goal condition requires at most 0.5 m
(`goal radius 0.35 m + vehicle radius 0.15 m`). D0 then ended in a
collision. This fixed candidate therefore did not satisfy even one
moving-cue D0 run. The D4 path curled in the start-side area and timed
out. The [path figure](../figures/dynamic_smoke_v0.png) depicts the two
saved software traces and cue schedule; the [live replay](live_preview.html)
lets the owner inspect every recorded observation and command while the
local preview server is running. From the repository root, run
`.venv\Scripts\python.exe -m http.server 8765 --bind 127.0.0.1` and open
`http://127.0.0.1:8765/docs/live_preview.html`. The page reads local
derived JSON; regenerate the fixtures first in a fresh checkout.

These two attempts do not estimate a success rate, compare populations,
or establish why the behavior failed. The earlier fixed-cue D0 success
is retained separately and does not override this moving-cue failure.
The center-only subtraction is still exact for the linear probe; that
property alone does not make a useful vehicle controller.

## Checks and next decision

- `tests/test_dynamic_smoke.py` passed two focused tests (exit 0) for
  deterministic replay, declared split/seed/scenarios, cue phase labels,
  observation schema, wheel bounds, a clean D0/D4 prefix, and the D4
  applied-motor change after onset.
- The full unittest suite passed 57 tests (exit 0) on 2026-09-29.
- `dynamic_smoke.py --verify-existing` and
  `render_dynamic_smoke.py --verify-existing` regenerate and compare the
  saved JSON and SVG byte for byte.
- P4 remains open. Before another numerical choice, decide whether the
  project should use the separately named unsigned structural model route
  proposed in `docs/p2_model_route_packet.md`, and define a versioned
  mapping and learning budget. Any response to this failure must be logged
  as a new candidate version, with training data and controls kept fair.
