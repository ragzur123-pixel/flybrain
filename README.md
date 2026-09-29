# FlyAI

FlyAI is a research project testing whether a small, anatomically derived *Drosophila* network can control a simulated two-wheel vehicle and recover from sensor or motor perturbations. The comparison is planned across the selected network, a matched random network, and a directed degree-preserving network.

**Status, 29 September 2026:** The publication-time FAFB v783 data products have passed local validation, a 119-neuron DNp20/DNp22 subnetwork has passed anatomical checks, and the independent 2D environment has passed software tests. A neural controller, adaptation methods, pilot results, and comparative results have **not** been validated. Synapse counts describe anatomy; they are not measured physiological weights. Vehicle sensors and motors are modeled interfaces, not demonstrated fly behavior.

## What is in this repository

| Path | Contents |
| --- | --- |
| `src/flyai/` | Data acquisition, validation, circuit extraction, audits, and vehicle environment code. |
| `tests/` | Synthetic software tests. They do not establish biological validity. |
| `configs/` | Versioned data, circuit, resource, and environment settings. |
| `data/raw/manifest.csv` | Provenance and hashes for local source downloads. Raw downloads are excluded from Git. |
| `docs/` | Methods, source evidence, decisions, and gate reviews. |
| `figures/` | Generated data and software previews. No figure is a controller performance result. |
| `protocol/`, `runs/`, `report/` | Reserved for a frozen protocol, recorded runs, and the eventual report. |

The [open issues](docs/issues.md) record unresolved research questions. The
[input-side route chart](figures/selected_side_routes.png) shows which
anatomical input sides can reach each selected descending output; it does not
establish a motor decoder. The [unsigned response preview](figures/unsigned_rate_probe_v0.png)
is an exploratory software calculation, not a selected neural model or
vehicle result. The [rate-to-wheel fixture preview](figures/decoder_fixture_v0.png)
shows one deterministic software episode and the center-cue bias under an
assumed decoder. A [second exploratory preview](figures/decoder_fixture_v1.png)
shows a center-only reference subtraction that removes that bias for the
current linear probe. Neither is a pilot or validated controller result.
The [moving-cue smoke preview](figures/dynamic_smoke_v0.png) records two
training-seed software attempts: D0 collided and D4 timed out. It is not
a performance estimate or a frozen-model result.

## Run the software tests

The local suite was run with Python 3.12. The test suite uses the standard library; data-processing scripts need the packages in `requirements-data.txt`.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-data.txt
.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py'
```

The P3 gate check passed 38 tests on 29 September 2026; the current full suite passed 57 after the sparse graph, side-route, unsigned response probe, decoder fixture, and moving-cue smoke checks. Some tests use generated fixtures when those files are available; a fresh clone may report a skip for a local fixture comparison. The [P3 gate review](docs/p3_gate_review_2026-09-29.md) records its exact verification commands and limits.

## Data and attribution

The source graph is the [FlyWire Consortium FAFB v783.0 archive](https://zenodo.org/records/10676866), with pinned product names and hashes in `configs/data_sources.json` and `data/raw/manifest.csv`. The [FlyWire public-release guidelines](https://home.flywire.ai/guidelines) state CC BY-NC 4.0 terms. Source files are not redistributed here. See [data and attribution](docs/data_and_attribution.md) before using the figures or downloading the archive.

## Research boundaries

The selected graph is an anatomical input to a proposed model. Unknown synaptic signs, the virtual sensor and motor mappings, and controller performance remain open. The [model route packet](docs/p2_model_route_packet.md), [environment contract](docs/environment_v1_contract.md), and [open issues](docs/issues.md) record those limits. Claims about adaptation or superiority require a frozen protocol and held-out runs; none are reported here.
