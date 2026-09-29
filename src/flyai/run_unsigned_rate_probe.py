"""Run three fixed unit-cue traces through the exploratory P4 rate probe."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.selected_graph import OUTPUT_KEYS, load_selected_graph
from flyai.unsigned_rate_probe import CHANNELS, UnsignedRateProbe


def make_report(workspace: Path) -> dict:
    config_path = workspace / "configs/unsigned_rate_probe_v0.yaml"
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    if config["version"] != 0 or not config["status"].startswith("exploratory P4"):
        raise ValueError("This runner requires the exploratory v0 config")
    schedule = config["probe_schedule"]
    on, off = schedule["stimulus_steps"], schedule["silence_steps"]
    if not isinstance(on, int) or not isinstance(off, int) or on <= 0 or off <= 0:
        raise ValueError("Probe on/off steps must be positive integers")
    if schedule["stimuli"] != list(CHANNELS):
        raise ValueError("Probe stimulus order changed")
    graph = load_selected_graph(workspace)
    labels = [f"{role} {side}" for role, side in OUTPUT_KEYS]
    if labels != config["output_order"]:
        raise ValueError("Probe output order changed")
    traces = []
    for stimulus in schedule["stimuli"]:
        probe = UnsignedRateProbe(graph, config)
        points = []
        for step in range(1, on + off + 1):
            observed = {side: float(side == stimulus and step <= on) for side in CHANNELS}
            response = probe.step(observed)
            points.append({"step": step, "cue": "on" if step <= on else "off",
                           "outputs": dict(zip(labels, response))})
        traces.append({"stimulus": stimulus, "points": points})
    return {
        "status": "exploratory unsigned software response; no neural or behavioral validation",
        "dataset": config["dataset"],
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "nodes_csv_sha256": graph.nodes_sha256,
        "edges_csv_sha256": graph.edges_sha256,
        "output_order": labels,
        "dt_s": probe.dt_s,
        "stimulus_steps": on,
        "silence_steps": off,
        "traces": traces,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()
    root = args.workspace.resolve()
    report = make_report(root)
    output = root / "data/derived/unsigned_rate_probe_v0.json"
    content = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    if args.verify_existing:
        if not output.exists() or output.read_bytes() != content:
            raise ValueError("Existing unsigned-rate probe trace differs")
    else:
        if output.exists():
            raise FileExistsError("Preserve existing unsigned-rate probe trace")
        output.write_bytes(content)
    print("PASS: three fixed cue traces; " +
          ("existing output unchanged" if args.verify_existing else "trace written"))


if __name__ == "__main__":
    main()
