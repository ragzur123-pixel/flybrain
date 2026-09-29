# Control-design note: simple rule and task adequacy

Status: **pre-freeze proposal, 2026-09-28**. This note changes neither the
P1 gate nor the planned 3-topology × 5-scenario × 3-adaptation main matrix.
It prepares a diagnostic reference and a pilot check before environment and
controller implementation.

## Source and limit

The author-run [FLY-lab comparison](https://github.com/Recluse/FLY-lab)
reports that its fly-connectome controller and a two-line left/right rule
both succeeded in all 30 test episodes per stimulus side on a simple
head-bristle turning task. The authors conclude their task could not separate
the two solvers, and explicitly list untested dynamic stimuli, noise,
dropouts, and navigation. Their measurements were **not reproduced here** and
their body/sensory setup differs from FlyAI's planned ocellar/2D task (FW-057).

The newer [FlyCNS preprint](https://arxiv.org/abs/2609.28816) uses BANC-derived
directional routing statistics as a weak prior for communication allocation in
quadruped locomotion. It does not use FlyAI's FAFB ocellar root-ID path or the
proposed post-damage weight-versus-edge-edit comparison, but it narrows any
broad claim that fly connectomes newly inform embodied control (FW-058).

## Diagnostic reference to specify before coding

- Add a transparent **simple orientation rule**: from the same declared
  left/right sensor values used by neural controllers, command a bounded turn
  toward the stronger cue and a fixed or separately declared forward speed.
  Tie, missing-channel, saturation, and no-cue behavior must be written in
  `configs/environment_v1.yaml` before seeing test outcomes.
- Give the rule the same observation stream, action limits, episode starts,
  cue sequences, perturbation schedule, and held-out test seeds as the
  connectome-based controller. It has no trainable synaptic graph; report that
  difference plainly instead of pretending parameter counts are matched.
- Treat it as a **diagnostic task reference**, not a fourth topology in the
  45S main matrix. The core topology/adaptation comparison remains real,
  random, and directed-degree-preserving graphs under equal budgets.
- A possible replayed-output control can test whether actions depend on the
  current cue, but it is an optional pilot diagnostic. It must not substitute
  for random/degree-preserving topology controls or for a simple rule.

## Pilot task-adequacy criterion to predeclare

The pilot should test at least one **time-varying cue sequence** beyond a
persistent single-side signal: for example, a side switch and cue loss within
the same episode, with timing generated independently of controller output.
Sensor noise/dropout belongs to the declared D scenarios. The task should
make reaction, recovery, overshoot, and path efficiency measurable rather than
only a binary left/right label. Exact sequences, timings, thresholds, and
success metrics remain pending P3/P6 decisions.

If the simple rule and all candidate neural controllers saturate the primary
metric on pilot conditions, mark that task **non-discriminating**. Redesign it
using pilot-only seeds before protocol freeze, or keep it and report no
detectable advantage. Never choose difficulty from final test outcomes. If
the rule wins, report that result. Do not claim biological superiority from a
model's graph structure or a visual demo alone.

## What remains open

The archive baseline and selected anatomical circuit are fixed. Virtual
neuron-to-motor mapping (ISSUE-001), neural dynamics (ISSUE-003), pilot
budgets (ISSUE-004), and novelty wording (ISSUE-005) remain open. The
independent P3 environment exists, but the simple rule and pilot task
adequacy check in this note are still proposals; no controller result
exists.
