# C03 anatomical path rule — predeclared 2026-09-28

This rule was written **before the new C03 raw-graph scan and before any
vehicle or controller exists**. The selected data lineage is the
publication-time 2024 FAFB v783 archive, with annotation tag `v2.1.0` and
291 provenance-checked candidate IDs (P1 pass; C02 inventory). The exact
machine-readable rule is `configs/path_feasibility_v1.json`.

- Treat each graph row as a directed presynaptic→postsynaptic observation.
  Sum `syn_count` across neuropil rows for an ordered pair *before* applying
  a threshold. Do not treat the reverse pair as the same connection.
- At a **primary screening minimum of five pair-summed synapses**, count
  one-edge photoreceptor→DNp28 and two-edge
  photoreceptor→OCG01→DNp20/DNp22 routes. Require every edge in a two-edge
  route to meet the same minimum. Repeat at minimum one as a sensitivity
  screen. Five is an analytical screening convention influenced by the
  current Codex display minimum (FW-004), **not** a published biological
  threshold for the archive or an assertion that smaller connections vanish.
- Report unique photoreceptor IDs separately by biological left, right, and
  center. Also report unique photoreceptors with a fully same-side route:
  direct photo and DNp28 share a side; for two-edge routes the photo, OCG01,
  and descending output all share a side. A photoreceptor reachable through
  multiple OCG01 cells is counted once per output. Do not silently remove
  opposite-side or center input from the all-side total.
- Mark a role **anatomically feasible for this screen** only if both its
  left and right outputs receive at least one fully same-side candidate
  photoreceptor at the stated threshold. This is a reachability check,
  not evidence of steering sign, neuron excitability, motor mapping, or
  a viable reduced network under resource limits.
- Retain right DNp28, which has `status=outlier_seg`, in the feasibility
  count but report the flag. C04 must decide whether it is suitable for a
  selected circuit. This C03 rule selects no root IDs or graph size.

The old exploratory screen's thresholds one and five were inspected while
writing this rule; the current C03 work will verify it against a fresh scan
of the checksum-pinned raw graph. No behavioral outcome was available to
influence the threshold. The owner will review any eventual C04 selection.
