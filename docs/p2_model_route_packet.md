# C07 model route packet — 2026-09-28

**Status: proposal, no dynamics or vehicle behavior selected.** The owner
selected the anatomical DNp20+DNp22 circuit. That choice does not fix its
neural dynamics or assign the four descending neurons to virtual motors.

## Observed constraints

- The selected archive graph has 119 nodes, 169 directed pairs and 4,434
  pair-summed synapses. It contains 103 photoreceptors (34 left, 36 right,
  33 center), 12 OCG01 cells (six per side), and four descending outputs
  (one DNp20 and one DNp22 per side). These are anatomical labels.
- The exact v783 annotation join predicts serotonin for 87 selected neurons,
  including 87 of the 103 photoreceptors. It provides **zero nonblank
  `known_nt` values** for this selection. The prediction authors report
  serotonin as their least reliable class and sensory mispredictions
  (FW-069–FW-071). Thus a direct signed-weight conversion cannot be called
  a measured synaptic model.
- The Shiu et al. LIF source used a v630 graph and a prepared signed
  `Excitatory x Connectivity` column; its author repository permits a
  different v783 input. It does not supply a validated weight or motor map
  for this exact 119-cell ocellar selection (FW-018–FW-027).

## Feasible routes to an exploratory software pilot

| Route | Explicit construction | What it can test | Main limit |
| --- | --- | --- | --- |
| A: Shiu-style signed LIF transfer | Multiply selected pair counts by a declared presynaptic sign and chosen `W_syn`; declare the rule for every predicted class, including serotonin, and test alternative sign policies. Use source equations with a recorded version and simulator time step. | Whether a specific *assumed* signed LIF model yields a stable cue-to-output response. | Predicted transmitter and receptor effects are unverified; published calibration and validation were on different circuits and a v630 graph. |
| B: unsigned structural dynamics | Keep directed counts as nonnegative structural priors; normalize under a declared rule, then use a separately named rate or spiking model with trainable signed gains. Never describe gains as biological excitation/inhibition. | Whether the selected topology helps in the proposed paired adaptation comparison under a consistent software model. | More engineered parameters and a different scientific claim; fairness of random/rewired controls and parameter budgets needs care. |
| C: anatomy-only result | Analyze reachability, laterality, robustness and edge perturbations without a vehicle controller. | A source-backed structural question if dynamic models prove untenable. | Does not answer the planned embodied adaptation question. |

**Recommendation for review:** route B is the most defensible first
*computational* pilot for the selected circuit because it keeps the
anatomical prior while making the unsupported signs explicit model
parameters. Route A can be a sensitivity analysis only after a complete
sign rule and calibrated/verified implementation exist. Route C is the
fallback if the pilot cannot produce a stable, informative D0 task. This
recommendation is an inference, not an owner decision or P2 pass.

An [exploratory unsigned response probe](p4_unsigned_rate_probe.md) checks
count normalization, side-matched inputs, latency, silence, and four named
readouts on the selected graph. Two [software decoder fixtures](p4_center_cancellation.md)
now test an uncorrected and a center-cancelled virtual wheel mapping. They
have no trainable signed gains or pilot result and do not select route B
for the project.

## Mapping contract to decide before implementation

The later [input-side route audit](selected_side_routes.md) recounts ordered
paths from left, center, and right photoreceptors into each named output.
The left DNp20 output receives 7/18/28 paths and left DNp22 receives
8/11/36, respectively. Thus an output's anatomical side alone does not
define a virtual steering direction. This is path reachability, not a
predicted response; all three route choices above retain that uncertainty.

1. **Inputs:** define an observable virtual cue with left/right/center
   values in a stated range and units. Assign every retained photoreceptor
   one input channel by its annotated side. A center input must have a
   declared symmetric or separate encoding; it must not be silently
   counted as a left or right motor channel. Specify deterministic or
   seeded stochastic spike/rate generation, onset, update order, and
   behavior when a cue is absent.
2. **Readouts:** compute four named values from the exact DNp20/DNp22
   root IDs in `configs/subnetwork_selection.yaml`. State the measurement
   interval, rate normalization, zero-activity behavior, and how the two
   output families are combined. A virtual steering sign is an engineered
   convention and must be checked under mirror-cue synthetic tests.
3. **Control:** define action bounds, speed/turn-rate units, clipping,
   latency, and how the same interface applies to real, random, and
   degree-preserving topologies. Avoid embedding goal position or damage
   labels in the sensor input.
4. **Weights:** specify count transform, normalization, signs or signed
   gains, bounds, initial values, learning permissions, and unknown-label
   treatment. Retain the raw positive pair counts and the exact node/edge
   hashes as separate immutable inputs.
5. **Verification:** before an embodied score, test mirroring, no-input,
   side-switch, cue-loss, output silence, saturation, reproducible seed,
   non-finite rejection, and identical sensor/action ranges across graph
   controls. An output movement on a synthetic fixture is software
   evidence only, not proof of biological function.

## Gate state

The P2 anatomical gate **passes** under the project guide's phase table.
The model route and virtual mapping belong to P4 and remain open until
fixed in a versioned config and tested. No route has been frozen or
behavior scored. Independent P3 environment work may proceed.
