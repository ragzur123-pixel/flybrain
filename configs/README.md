# Configurations

These files describe the currently selected data products, anatomical extraction rules, resource limits, and pre-freeze vehicle environment. JSON syntax is used where a `.yaml` file is parsed by the Python standard library.

| File | Role |
| --- | --- |
| `data_sources.json` | Pinned FAFB v783 download products and publisher checksums. |
| `resources.yaml` | Acquisition and processing limits. |
| `path_feasibility_v1.json` | Anatomical path-screen rules. |
| `subnetwork_selection.yaml` | Selected DNp20/DNp22 extraction rule. |
| `environment_v1.yaml` | Pre-freeze 2D task, D0–D4 perturbations, seed pools, and dynamic cue. |
| `environment_fixture_2026-09-28.yaml` | Exact historical config used to verify the fixed-command preview. |

The selected anatomical rule does not define a signed neural model. Before changing a scientific parameter, update `docs/protocol_changes.md` and its affected gate or protocol record. After protocol freeze, create a new version rather than altering settings tied to completed runs.
