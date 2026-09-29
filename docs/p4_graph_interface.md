# P4 sparse anatomy interface — 2026-09-29

**Status: verified software input to P4, not a neural model.**
`load_selected_graph(workspace)` in `src/flyai/selected_graph.py` reads the
owner-selected 2024 FAFB v783 CSVs under `data/derived/` and the fixed C04
selection config. It checks SHA-256 values in the extraction report before
parsing, then validates schema, unique root IDs and pairs, metadata, directed
role order, positive thresholded pair counts, all four bilateral outputs, and
reachability to an output. It fails closed on mismatches.

The immutable `SelectedGraph` holds 119 `Node` records and 169 sparse `Edge`
records. Each edge stores source and target node indices and the observed
`pair_synapses` count. `input_indices(side)` selects photoreceptors by annotated
left, center, or right side. `outputs` maps `(DNp20|DNp22, left|right)` to each
output index. The loaded graph sums to 4,434 pair-summed synapses.

These labels are anatomy metadata. `pair_synapses` is neither a physiological
strength nor a signed model weight. The interface does not assign a virtual
sensor channel, neural equation, transmitter sign, learning rule, or wheel
command. Those choices remain P4 work under `docs/p2_model_route_packet.md`
and `ISSUE-003`.

Verification: `.venv\Scripts\python.exe -m unittest discover -s tests -p
'test_selected_graph.py' -v` passed three tests. The tests load the real
selection, reject a byte-tampered CSV, and reject inconsistent edge-role
metadata even when its CSV checksum is updated. The real-load test confirms
119 nodes, 169 edges, 4,434 pair counts, center inputs, and four named outputs.
