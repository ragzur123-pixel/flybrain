# FlyAI visual previews

Status: the 2024 publication-time FAFB v783 archive is the selected main
baseline and its [P1 gate](p1_archive_gate_review_2026-09-28.md) passed.
The vehicle view shows a fixed-command software fixture; the other views show anatomy and
data checks. None shows neural activity or a completed experiment.

## Interactive 3D neurons

[Open the left/right DNp28 pair in Neuroglancer](<https://neuroglancer-demo.appspot.com/#!%7B%22title%22%3A%22FlyAI%20v783%20candidate%20DNp28%20left%2Fright%20(anatomy%20only)%22%2C%22dimensions%22%3A%7B%22x%22%3A%5B4e-9%2C%22m%22%5D%2C%22y%22%3A%5B4e-9%2C%22m%22%5D%2C%22z%22%3A%5B4e-8%2C%22m%22%5D%7D%2C%22position%22%3A%5B132876.5%2C34570.5%2C4098.5%5D%2C%22crossSectionScale%22%3A1%2C%22projectionScale%22%3A17850%2C%22layers%22%3A%5B%7B%22type%22%3A%22segmentation%22%2C%22source%22%3A%5B%7B%22url%22%3A%22precomputed%3A%2F%2Fgs%3A%2F%2Fflywire_v141_m783%22%2C%22subsources%22%3A%7B%22default%22%3Atrue%2C%22mesh%22%3Atrue%7D%2C%22enableDefaultSubsources%22%3Afalse%7D%2C%22precomputed%3A%2F%2Fhttps%3A%2F%2Fflyem.mrc-lmb.cam.ac.uk%2Fflyconnectome%2Fann%2Fflytable-info-783%22%5D%2C%22tab%22%3A%22segments%22%2C%22segments%22%3A%5B%22720575940621561697%22%2C%22720575940640142141%22%5D%2C%22segmentQuery%22%3A%22DNp28%22%2C%22segmentColors%22%3A%7B%22720575940621561697%22%3A%22%23ff4eb8%22%2C%22720575940640142141%22%3A%22%2335d8ff%22%7D%2C%22name%22%3A%22flywire%22%7D%2C%7B%22type%22%3A%22segmentation%22%2C%22source%22%3A%22precomputed%3A%2F%2Fhttps%3A%2F%2Fflyem.mrc-lmb.cam.ac.uk%2Fflyconnectome%2Fbrain_mesh%22%2C%22tab%22%3A%22source%22%2C%22objectAlpha%22%3A0.12%2C%22segments%22%3A%5B%220%22%2C%221%22%5D%2C%22segmentColors%22%3A%7B%220%22%3A%22%23555555%22%2C%221%22%3A%22%23555555%22%7D%2C%22name%22%3A%22brain%22%7D%5D%2C%22selectedLayer%22%3A%7B%22visible%22%3Atrue%2C%22layer%22%3A%22flywire%22%7D%2C%22layout%22%3A%223d%22%2C%22uiControlVisibility%22%3A%7B%7D%7D>).
The left candidate is magenta (root ID `720575940621561697`); the right
candidate is cyan (root ID `720575940640142141`). Both IDs are from the
pinned v783 annotation/proofread packet. The right cell has the annotation
status `outlier_seg`, so the 3D view does not settle its suitability.
Rotating and zooming the view changes only the camera, not the graph analysis.
The 2026-09-28 UI check showed both DNp28 entries visible (2/2) and both
colored neuron meshes rendered in the 3D pane. This view cannot display
the project's percentage complete or prove the vehicle is working.

## Local checked previews

- [Deterministic 2D vehicle fixture](../figures/environment_fixture.png):
  the same fixed wheel command in D0 and D4. The cyan path reaches the
  virtual goal; the pink path shows the declared right-motor gain change.
  This checks environment mechanics only. It uses no neural controller,
  learning, or connectome output (`docs/environment_v1_contract.md`).
- [Selected transmitter predictions](../figures/selected_neurotransmitter_audit.png):
  the exact 119-ID annotation join split by predicted class for neurons,
  outgoing directed connections, and pair-summed synapses. None of the
  selected neurons has a nonblank `known_nt` value. This is a prediction
  coverage chart, not a neural activity or signed-weight figure;
  `docs/selected_neurotransmitter_audit.md` gives the numbers and caveats.
- [Selected DNp20+DNp22 graph schematic](../figures/selected_subnetwork.png):
  the actual 119 selected neurons and 169 directed archive connections.
  Layout is diagrammatic; magenta/cyan/gold show biological left/right/center,
  and curves point from input toward output. It shows connectivity, not
  activity, motion, or a motor sign.
- [C03 anatomical path sensitivity](../figures/path_feasibility_v1.png):
  all six candidate descending outputs at pair minimums one and five.
  Teal counts unique photoreceptors with a fully same-side path; gray
  counts the other unique reachable inputs. The paired values are a
  reachability screen, not neural activity or vehicle performance.
- [Side-resolved candidate pathways](../figures/ocellar_laterality.png):
  archive-derived input counts by biological side, not behavior.
- [Archive-family consistency](../figures/archive_aggregate_check.png):
  56 comparable neuron/region subtotals obey the expected bound; two
  `UNASGD` rows have no aggregate counterpart.
- [Archive versus current Codex](../figures/codex_reconciliation.png):
  all ten checked connection counts differ between these products.

The [open issues](issues.md) record the remaining work.
