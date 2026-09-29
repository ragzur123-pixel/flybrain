"""Two predeclared moving-cue software smoke attempts on a train seed."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.center_cancelled_decoder import CenterCancelledDecoder
from flyai.selected_graph import load_selected_graph
from flyai.vehicle_env import VirtualVehicle


def cue_at_step(schedule: list[dict], step: int) -> str:
    source = schedule[0]["source"]
    for item in schedule:
        if step < item["step"]:
            break
        source = item["source"]
    return source


def run_smoke(workspace: Path) -> dict:
    paths = [workspace / relative for relative in (
        "configs/dynamic_smoke_v0.yaml", "configs/decoder_fixture_v1.yaml",
        "configs/unsigned_rate_probe_v0.yaml", "configs/environment_v1.yaml")]
    smoke_bytes, controller_bytes, probe_bytes, environment_bytes = (
        path.read_bytes() for path in paths)
    smoke, controller, probe, environment = (
        json.loads(content) for content in
        (smoke_bytes, controller_bytes, probe_bytes, environment_bytes))
    if smoke["version"] != 0 or not smoke["status"].startswith("exploratory P4"):
        raise ValueError("Only exploratory dynamic smoke v0 is supported")
    if (smoke["controller_config"], smoke["probe_config"],
            smoke["environment_config"]) != tuple(str(path.relative_to(workspace)).replace("\\", "/")
                                                for path in paths[1:]):
        raise ValueError("Dynamic smoke dependency path changed")
    if smoke["split"] != "train" or smoke["scenarios"] != ["D0", "D4"] or \
            smoke["start_pose"] != "environment default for the named split and seed":
        raise ValueError("Dynamic smoke scope changed")
    if controller["version"] != 1 or probe["dt_s"] != environment["dt_s"]:
        raise ValueError("Controller version or time step changed")
    graph = load_selected_graph(workspace)
    schedule = environment["episode_design"]["dynamic_cue"]["schedule"]
    runs = []
    for scenario in smoke["scenarios"]:
        env = VirtualVehicle(environment)
        decoder = CenterCancelledDecoder(graph, probe, controller)
        observation, _ = env.reset(smoke["seed"], scenario, split=smoke["split"])
        path = [{"step": 0, "cue_source": cue_at_step(schedule, 0),
                 "observation": observation, "pose": env.pose_for_logging(),
                 "full_outputs": [0.0] * 4, "center_reference_outputs": [0.0] * 4,
                 "raw_score": 0.0, "center_score": 0.0, "corrected_score": 0.0,
                 "command_m_s": [0.0, 0.0], "applied_wheels_m_s": [0.0, 0.0]}]
        while True:
            result = decoder.step(observation)
            observation, _, terminal, truncated, info = env.step(result["command_m_s"])
            path.append({"step": env.steps,
                         "cue_source": cue_at_step(schedule, env.steps),
                         "observation": observation, "pose": env.pose_for_logging(),
                         **result,
                         "applied_wheels_m_s": env.applied_wheel_speeds_for_logging()})
            if terminal or truncated:
                break
        runs.append({"scenario": scenario, "split": smoke["split"],
                     "seed": smoke["seed"], "map": env.map_for_logging(),
                     "steps": env.steps, "termination_reason": info["status"],
                     "observed_cue_phases": list(dict.fromkeys(point["cue_source"]
                                                            for point in path)),
                     "path": path})
    return {
        "status": "exploratory P4 software smoke; no model selection, pilot, or final result",
        "dataset": smoke["dataset"],
        "config_sha256": hashlib.sha256(smoke_bytes).hexdigest(),
        "controller_config_sha256": hashlib.sha256(controller_bytes).hexdigest(),
        "probe_config_sha256": hashlib.sha256(probe_bytes).hexdigest(),
        "environment_config_sha256": hashlib.sha256(environment_bytes).hexdigest(),
        "nodes_csv_sha256": graph.nodes_sha256,
        "edges_csv_sha256": graph.edges_sha256,
        "split": smoke["split"], "seed": smoke["seed"],
        "cue_schedule": schedule, "runs": runs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()
    root = args.workspace.resolve()
    report = run_smoke(root)
    output = root / "data/derived/dynamic_smoke_v0.json"
    content = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    if args.verify_existing:
        if not output.exists() or output.read_bytes() != content:
            raise ValueError("Existing dynamic smoke output differs")
    else:
        if output.exists():
            raise FileExistsError("Preserve existing dynamic smoke output")
        output.write_bytes(content)
    print("PASS: " + ", ".join(f"{run['scenario']} {run['termination_reason']} "
                             f"at step {run['steps']}" for run in report["runs"]))


if __name__ == "__main__":
    main()
