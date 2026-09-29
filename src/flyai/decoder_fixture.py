"""Exploratory rate-to-wheel software fixture, outside the selected P4 protocol."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from flyai.selected_graph import OUTPUT_KEYS, load_selected_graph
from flyai.unsigned_rate_probe import UnsignedRateProbe
from flyai.vehicle_env import VirtualVehicle, clamp


EXPECTED_OUTPUTS = [f"{role} {side}" for role, side in OUTPUT_KEYS]


def decode_wheels(outputs: tuple[float, ...], config: dict) -> tuple[float, float]:
    """Map four *modeled* unsigned rates to virtual wheel speeds."""
    if config["output_order"] != EXPECTED_OUTPUTS:
        raise ValueError("Decoder output order changed")
    if len(outputs) != 4 or any(isinstance(value, bool) or
                                not isinstance(value, (int, float)) or
                                not math.isfinite(value) or not 0 <= value <= 1
                                for value in outputs):
        raise ValueError("Decoder requires four finite unit-interval outputs")
    base = float(config["base_speed_m_s"])
    gain = float(config["gain_m_s_per_rate_unit"])
    if not math.isfinite(base) or not math.isfinite(gain) or not 0 <= base <= 1 or gain < 0:
        raise ValueError("Decoder base/gain invalid")
    opponent = (outputs[0] + outputs[2] - outputs[1] - outputs[3]) / 2
    return clamp(base - gain * opponent, 0, 1), clamp(base + gain * opponent, 0, 1)


def run_fixture(workspace: Path) -> dict:
    """Run one deterministic D0 fixture; no training, selection, or pilot metrics."""
    decoder_path = workspace / "configs/decoder_fixture_v0.yaml"
    probe_path = workspace / "configs/unsigned_rate_probe_v0.yaml"
    env_path = workspace / "configs/environment_v1.yaml"
    config_bytes, probe_bytes, env_bytes = (path.read_bytes() for path in
                                            (decoder_path, probe_path, env_path))
    config, probe_config = json.loads(config_bytes), json.loads(probe_bytes)
    if config["version"] != 0 or not config["status"].startswith("exploratory"):
        raise ValueError("Only the exploratory v0 decoder is supported")
    if config["rate_probe_config"] != "configs/unsigned_rate_probe_v0.yaml" or \
            config["vehicle_config"] != "configs/environment_v1.yaml":
        raise ValueError("Decoder dependency path changed")
    graph = load_selected_graph(workspace)
    probe = UnsignedRateProbe(graph, probe_config)
    env = VirtualVehicle.from_file(env_path)
    fixture = config["fixture"]
    if fixture["scenario"] != "D0" or fixture["split"] != "fixture":
        raise ValueError("This runner is restricted to the D0 software fixture")
    observation, _ = env.reset(fixture["seed"], fixture["scenario"],
                               split=fixture["split"], start_pose=tuple(fixture["start_pose"]))
    path = [{"step": 0, "pose": env.pose_for_logging(),
             "observation": observation, "outputs": [0.0] * 4,
             "command_m_s": [0.0, 0.0]}]
    while True:
        outputs = probe.step(observation)
        command = decode_wheels(outputs, config)
        observation, _, terminal, truncated, info = env.step(command)
        path.append({"step": env.steps, "pose": env.pose_for_logging(),
                     "observation": observation, "outputs": outputs,
                     "command_m_s": command})
        if terminal or truncated:
            break
    return {
        "status": "exploratory software fixture; no pilot or biological behavior result",
        "dataset": config["dataset"],
        "decoder_config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "probe_config_sha256": hashlib.sha256(probe_bytes).hexdigest(),
        "vehicle_config_sha256": hashlib.sha256(env_bytes).hexdigest(),
        "nodes_csv_sha256": graph.nodes_sha256,
        "edges_csv_sha256": graph.edges_sha256,
        "scenario": fixture["scenario"], "split": fixture["split"],
        "seed": fixture["seed"], "start_pose": fixture["start_pose"],
        "steps": env.steps, "termination_reason": info["status"], "path": path,
    }
