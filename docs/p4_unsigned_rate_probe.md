# Exploratory unsigned response probe — 2026-09-29

**Status: software probe only.** This is a candidate calculation to inspect
the selected graph's response to virtual side channels. Rüzgar has not chosen
a P4 neural model. This probe does not implement the published signed LIF
model, a trainable controller, a motor decoder, or a vehicle episode.

## Declared assumptions and update

The pre-run config is `configs/unsigned_rate_probe_v0.yaml` (SHA-256
`ddc2a4fa29ae51d48e54ced6ba816bc060fcba3dfb48c686749baeb97f46941b`).
It pins the selected v783 node and edge CSV hashes. All numerical choices
here are **ASSUMPTION**, not measurements of fly physiology.

- Each annotated left, center, or right photoreceptor receives the matching
  virtual input value in `[0,1]` immediately. No pose, goal, scenario, or
  reward enters the probe.
- Each directed pair count is divided by the total incoming pair count at
  its postsynaptic node. These nonnegative coefficients sum to one per
  OCG01/output node. No transmitter or receptor sign is assigned.
- With `alpha=0.5` and `dt=0.1 s`, each OCG01 state is
  `r_new=(1-alpha)*r_old+alpha*sum(w*current_photo)`.
  Each descending state uses the **previous** OCG01 state in the same
  equation. All states start at zero; output order is DNp20 left/right,
  then DNp22 left/right. There are no recurrent edges, trainable gains,
  spikes, or delays inferred from biology.
- The implementation holds one state per selected node and sparse incoming
  lists. Storage grows with `N+E` (119 nodes, 169 directed edges); it does
  not allocate a dense connectome matrix.

## Fixed software check

For each side separately, the runner applies unit input for 12 steps and
then zero input for 12 steps, resetting all state between sides. The saved
trace is `data/derived/unsigned_rate_probe_v0.json` (SHA-256
`cf5aa5d645b38c06830c340254cd478fd3089a65cb1910a5426ea3d4dcc0bccc`).
At step 12, the four modeled outputs are:

| Cue side | DNp20 left | DNp20 right | DNp22 left | DNp22 right |
| --- | ---: | ---: | ---: | ---: |
| left | 0.4475 | 0.2071 | 0.5136 | 0.3713 |
| center | 0.3734 | 0.1762 | 0.1640 | 0.1956 |
| right | 0.1759 | 0.6136 | 0.3192 | 0.4299 |

These are **modeled software rates**, not observed neuron responses. They
also show why anatomical path counts alone do not specify response
amplitudes: the chosen count normalization and state rule affect the values.
The center cue produces unequal left/right outputs under these assumptions.
No steering direction or task success follows from this table.

The [trace preview](../figures/unsigned_rate_probe_v0.png) shows the rise,
one-step relay lag, and decay under cue loss. Its SVG generator is
`src/flyai/render_unsigned_rate_probe.py`; the trace generator is
`src/flyai/run_unsigned_rate_probe.py`.

## Verification and remaining work

- `.venv\Scripts\python.exe -m unittest discover -s tests -p
  'test_unsigned_rate_probe.py' -v`: 4 tests passed, exit 0. They check
  sparse direction, count normalization, latency, reset/replay, silence,
  invalid input transactionality, state bounds, and selected graph hashes.
- Both generators support `--verify-existing` for bytewise rerun checks.
- P4 still needs an owner-selected model route, a versioned numerical
  contract with justified parameters, a virtual sensor/motor mapping,
  learning policy, end-to-end episode, and gate review. No pilot or final
  result has been produced.
