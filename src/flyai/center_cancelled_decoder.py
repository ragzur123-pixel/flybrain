"""Exploratory dual-probe center cancellation and one software fixture."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from pathlib import Path

from flyai.selected_graph import OUTPUT_KEYS, SelectedGraph, load_selected_graph
from flyai.unsigned_rate_probe import UnsignedRateProbe
from flyai.vehicle_env import VirtualVehicle, clamp


OUTPUT_LABELS = [f"{role} {side}" for role, side in OUTPUT_KEYS]


def opponent(outputs: tuple[float, float, float, float]) -> float:
    return (outputs[0] + outputs[2] - outputs[1] - outputs[3]) / 2


class CenterCancelledDecoder:
    """Subtract a center-only reference from this *linear software probe*."""

    def __init__(self, graph: SelectedGraph, probe_config: dict, decoder_config: dict):
        if decoder_config["version"] != 1 or decoder_config["output_order"] != OUTPUT_LABELS:
            raise ValueError("Center-cancelled decoder config/version changed")
        base, gain = (decoder_config[key] for key in
                      ("base_speed_m_s", "gain_m_s_per_rate_unit"))
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) or
               not math.isfinite(value) for value in (base, gain)) or \
                not 0 <= base <= 1 or gain < 0:
            raise ValueError("Decoder base/gain invalid")
        self.base = float(base)
        self.gain = float(gain)
        self.full = UnsignedRateProbe(graph, probe_config)
        self.center_reference = UnsignedRateProbe(graph, probe_config)

    def reset(self) -> None:
        self.full.reset()
        self.center_reference.reset()

    def step(self, observation: Mapping[str, float]) -> dict:
        full_outputs = self.full.step(observation)
        center_outputs = self.center_reference.step({
            "left": 0.0, "center": observation["center"], "right": 0.0})
        raw = opponent(full_outputs)
        center = opponent(center_outputs)
        corrected = raw - center
        action = (clamp(self.base - self.gain * corrected, 0, 1),
                  clamp(self.base + self.gain * corrected, 0, 1))
        if not all(math.isfinite(value) for value in (*action, corrected)):
            raise ValueError("Decoder produced non-finite output")
        return {"full_outputs": full_outputs, "center_reference_outputs": center_outputs,
                "raw_score": raw, "center_score": center,
                "corrected_score": corrected, "command_m_s": action}


def run_fixture(workspace: Path) -> dict:
    """Run one deterministic D0 fixture using observations only for control."""
    decoder_path = workspace / "configs/decoder_fixture_v1.yaml"
    probe_path = workspace / "configs/unsigned_rate_probe_v0.yaml"
    vehicle_path = workspace / "configs/environment_v1.yaml"
    decoder_bytes, probe_bytes, vehicle_bytes = (path.read_bytes() for path in
                                                  (decoder_path, probe_path, vehicle_path))
    config, probe_config = json.loads(decoder_bytes), json.loads(probe_bytes)
    if config["version"] != 1 or not config["status"].startswith("exploratory"):
        raise ValueError("Only exploratory decoder fixture v1 is supported")
    if config["rate_probe_config"] != "configs/unsigned_rate_probe_v0.yaml" or \
            config["vehicle_config"] != "configs/environment_v1.yaml":
        raise ValueError("Decoder dependency path changed")
    fixture = config["fixture"]
    if fixture["scenario"] != "D0" or fixture["split"] != "fixture":
        raise ValueError("This runner is restricted to the D0 software fixture")
    graph = load_selected_graph(workspace)
    decoder = CenterCancelledDecoder(graph, probe_config, config)
    env = VirtualVehicle.from_file(vehicle_path)
    if probe_config["dt_s"] != env.config["dt_s"]:
        raise ValueError("Probe and vehicle time steps differ")
    vehicle = env.config["vehicle"]
    if (vehicle["min_wheel_speed_m_s"], vehicle["max_wheel_speed_m_s"]) != (0.0, 1.0):
        raise ValueError("Vehicle wheel bounds differ from decoder contract")
    observation, _ = env.reset(fixture["seed"], fixture["scenario"],
                               split=fixture["split"], start_pose=tuple(fixture["start_pose"]))
    path = [{"step": 0, "pose": env.pose_for_logging(), "observation": observation,
             "full_outputs": [0.0] * 4, "center_reference_outputs": [0.0] * 4,
             "raw_score": 0.0, "center_score": 0.0, "corrected_score": 0.0,
             "command_m_s": [0.0, 0.0]}]
    while True:
        result = decoder.step(observation)
        observation, _, terminal, truncated, info = env.step(result["command_m_s"])
        path.append({"step": env.steps, "pose": env.pose_for_logging(),
                     "observation": observation, **result})
        if terminal or truncated:
            break
    return {
        "status": "exploratory center-cancelled software fixture; no pilot or biological behavior result",
        "dataset": config["dataset"],
        "decoder_config_sha256": hashlib.sha256(decoder_bytes).hexdigest(),
        "probe_config_sha256": hashlib.sha256(probe_bytes).hexdigest(),
        "vehicle_config_sha256": hashlib.sha256(vehicle_bytes).hexdigest(),
        "nodes_csv_sha256": graph.nodes_sha256,
        "edges_csv_sha256": graph.edges_sha256,
        "scenario": fixture["scenario"], "split": fixture["split"],
        "seed": fixture["seed"], "start_pose": fixture["start_pose"],
        "steps": env.steps, "termination_reason": info["status"], "path": path,
    }
