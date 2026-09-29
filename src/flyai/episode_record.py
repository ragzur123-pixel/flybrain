"""Guide-schema episode records for deterministic environment fixtures."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

if not __package__:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.vehicle_env import VirtualVehicle


EPISODE_FIELDS = ("run_id", "episode_id", "split", "scenario", "seed_group",
                  "success", "steps", "collisions", "path_length",
                  "shortest_valid_path", "return", "termination_reason", "wall_seconds")


def run_fixed_command(config_path: Path, *, scenario: str, episode_id: int) -> dict:
    """Synthetic fixture, not a neural-controller or pilot experiment."""
    env = VirtualVehicle.from_file(config_path)
    env.reset(1, scenario, start_pose=(2.0, 5.0, 0.0))
    previous = env.pose_for_logging()
    path_length = 0.0
    total_reward = 0.0
    start_time = time.perf_counter()
    while True:
        _, reward, terminal, truncated, info = env.step((0.7, 0.7))
        current = env.pose_for_logging()
        path_length += math.hypot(current[0] - previous[0], current[1] - previous[1])
        previous = current
        total_reward += reward
        if terminal or truncated:
            break
    return {"run_id": f"fixture_v1__fixed_action__{scenario.lower()}__s0001",
            "episode_id": episode_id, "split": "fixture", "scenario": scenario,
            "seed_group": "fixture_s0001", "success": int(info["status"] == "goal"),
            "steps": env.steps, "collisions": int(info["status"] == "collision"),
            "path_length": round(path_length, 9),
            "shortest_valid_path": "",  # unavailable until a validated obstacle-aware path method exists
            "return": round(total_reward, 9), "termination_reason": info["status"],
            "wall_seconds": time.perf_counter() - start_time}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    output = root / "data/derived/environment_episodes_fixture.csv"
    config = root / "configs/environment_v1.yaml"
    rows = [run_fixed_command(config, scenario=s, episode_id=i)
            for i, s in enumerate(("D0", "D4"))]
    with output.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=EPISODE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"path": str(output),
                      "outcomes": [(row["scenario"], row["termination_reason"], row["steps"]) for row in rows]}))


if __name__ == "__main__":
    main()
