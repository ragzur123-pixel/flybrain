"""Deterministic pre-freeze 2D vehicle environment, separate from neural control."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path


SCENARIOS = frozenset({"D0", "D1", "D2", "D3", "D4"})
CHANNELS = ("left", "center", "right")


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def wrap_angle(angle: float) -> float:
    return (angle + math.pi) % (2 * math.pi) - math.pi


class VirtualVehicle:
    """Stepwise light-cue task; all numerical values are config assumptions."""

    def __init__(self, config: dict):
        if config["sensors"]["order"] != list(CHANNELS):
            raise ValueError("Sensor order must be left, center, right")
        if config["dt_s"] <= 0 or config["max_steps"] <= 0:
            raise ValueError("Time step and maximum steps must be positive")
        if config["vehicle"]["wheel_base_m"] <= 0:
            raise ValueError("Wheel base must be positive")
        design = config.get("episode_design")
        if design is not None:
            offsets = design["map_y_offsets_m"]
            if not offsets or not all(isinstance(value, (int, float)) and math.isfinite(value)
                                      for value in offsets):
                raise ValueError("Map offsets must be nonempty and finite")
            ranges = list(design["split_seed_ranges_inclusive"].values())
            if any(len(pair) != 2 or pair[0] > pair[1] for pair in ranges):
                raise ValueError("Each split needs an increasing seed range")
            if any(max(a[0], b[0]) <= min(a[1], b[1])
                   for i, a in enumerate(ranges) for b in ranges[i + 1:]):
                raise ValueError("Split seed ranges must not overlap")
            schedule = design["dynamic_cue"]["schedule"]
            if not schedule or schedule[0]["step"] != 0 or any(
                    later["step"] <= earlier["step"]
                    for earlier, later in zip(schedule, schedule[1:])):
                raise ValueError("Cue schedule must begin at zero and increase")
            if any(item["source"] not in {"goal", "upper", "lower", "off"}
                   for item in schedule):
                raise ValueError("Unknown cue source")
        self.config = config
        self._active = False

    @classmethod
    def from_file(cls, path: Path) -> "VirtualVehicle":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def reset(self, seed: int, scenario: str = "D0", *, split: str = "fixture",
              start_pose: tuple[float, float, float] | None = None):
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario}")
        if not isinstance(seed, int) or seed < 0:
            raise ValueError("Seed must be a nonnegative integer")
        cfg = self.config
        design = cfg.get("episode_design")
        if split == "fixture":
            y_offset = 0.0
        else:
            if design is None:
                raise ValueError("Legacy fixture config supports fixture episodes only")
            bounds = design["split_seed_ranges_inclusive"].get(split)
            if bounds is None or not bounds[0] <= seed <= bounds[1]:
                raise ValueError("Seed is outside the declared split range")
            y_offset = random.Random(seed ^ design["map_seed_xor"]).choice(
                design["map_y_offsets_m"])
        self._split = split
        self._map_y_offset = y_offset
        self._goal_y = cfg["goal"]["y_m"] + y_offset
        self._heading_rng = random.Random(seed)
        self._noise_rng = random.Random(seed ^ 0x5EED5EED)
        start = cfg["start"]
        if start_pose is None:
            pose = (start["x_m"], start["y_m"] + y_offset,
                    self._heading_rng.uniform(start["heading_min_rad"], start["heading_max_rad"]))
        else:
            pose = tuple(float(v) for v in start_pose)
        if len(pose) != 3 or not all(math.isfinite(v) for v in pose):
            raise ValueError("Start pose must contain three finite values")
        self.x, self.y, self.heading = pose[0], pose[1], wrap_angle(pose[2])
        if self._collides(self.x, self.y):
            raise ValueError("Start pose collides with world")
        self.scenario = scenario
        self.steps = 0
        if hasattr(self, "_last_applied_wheel_speeds"):
            del self._last_applied_wheel_speeds
        self._active = True
        return self._observation(), {"step": self.steps, "status": "running"}

    def _collides(self, x: float, y: float) -> bool:
        world = self.config["world"]
        radius = world["vehicle_radius_m"]
        if x - radius < 0 or y - radius < 0 or x + radius > world["width_m"] or y + radius > world["height_m"]:
            return True
        for obstacle in world["obstacles"]:
            nearest_x = clamp(x, obstacle["x_min"], obstacle["x_max"])
            nearest_y = clamp(y, obstacle["y_min"], obstacle["y_max"])
            if (x - nearest_x) ** 2 + (y - nearest_y) ** 2 <= radius ** 2:
                return True
        return False

    def _observation(self) -> dict[str, float]:
        cfg = self.config
        goal = cfg["goal"]
        sensors = cfg["sensors"]
        source = "goal"
        if self._split != "fixture":
            for item in cfg["episode_design"]["dynamic_cue"]["schedule"]:
                if self.steps < item["step"]:
                    break
                source = item["source"]
        if source == "off":
            values = dict.fromkeys(CHANNELS, 0.0)
        else:
            cue_y = self._goal_y
            if source == "upper":
                cue_y += cfg["episode_design"]["dynamic_cue"]["upper_y_offset_m"]
            elif source == "lower":
                cue_y += cfg["episode_design"]["dynamic_cue"]["lower_y_offset_m"]
            dx, dy = goal["x_m"] - self.x, cue_y - self.y
            bearing = math.atan2(dy, dx)
            d2 = dx * dx + dy * dy
            attenuation = 1 / (1 + sensors["distance_scale_per_m2"] * d2)
            values = {name: clamp(max(0.0, math.cos(wrap_angle(bearing - self.heading - sensors["offset_rad"][name]))) ** sensors["angular_power"] * attenuation, 0.0, 1.0)
                      for name in CHANNELS}
        if self.steps >= cfg["perturbations"]["onset_step"]:
            perturb = cfg["perturbations"]
            if self.scenario == "D1":
                values = {name: clamp(value + self._noise_rng.gauss(0, perturb["D1_sensor_noise_std"]), 0.0, 1.0)
                          for name, value in values.items()}
            elif self.scenario == "D2":
                values[perturb["D2_lost_channel"]] = sensors["missing_channel_value"]
            elif self.scenario == "D3":
                left, right = perturb["D3_swap_channels"]
                values[left], values[right] = values[right], values[left]
        return values

    def step(self, action: tuple[float, float] | list[float]):
        if not self._active:
            raise RuntimeError("Reset before stepping, or episode already ended")
        if len(action) != 2:
            raise ValueError("Action requires left and right wheel speeds")
        left, right = (float(value) for value in action)
        if not math.isfinite(left) or not math.isfinite(right):
            raise ValueError("Action must be finite")
        cfg = self.config
        vehicle = cfg["vehicle"]
        low, high = vehicle["min_wheel_speed_m_s"], vehicle["max_wheel_speed_m_s"]
        left, right = clamp(left, low, high), clamp(right, low, high)
        if self.scenario == "D4" and self.steps >= cfg["perturbations"]["onset_step"]:
            right *= cfg["perturbations"]["D4_right_motor_gain"]
        self._last_applied_wheel_speeds = (left, right)
        dt = cfg["dt_s"]
        forward = (left + right) / 2
        omega = (right - left) / vehicle["wheel_base_m"]
        next_x = self.x + forward * math.cos(self.heading) * dt
        next_y = self.y + forward * math.sin(self.heading) * dt
        collision = self._collides(next_x, next_y)
        if not collision:
            self.x, self.y = next_x, next_y
            self.heading = wrap_angle(self.heading + omega * dt)
        self.steps += 1
        goal = cfg["goal"]
        reached = math.hypot(self.x - goal["x_m"], self.y - self._goal_y) <= goal["radius_m"] + cfg["world"]["vehicle_radius_m"]
        timeout = self.steps >= cfg["max_steps"]
        if collision:
            status = "collision"
        elif reached:
            status = "goal"
        elif timeout:
            status = "timeout"
        else:
            status = "running"
        self._active = status == "running"
        reward = cfg["reward"]["step"] + (cfg["reward"][status] if status != "running" else 0.0)
        return self._observation(), reward, status in ("collision", "goal"), status == "timeout", {
            "step": self.steps, "status": status}

    def pose_for_logging(self) -> tuple[float, float, float]:
        """Episode logger only. The controller must receive observation alone."""
        if not hasattr(self, "steps"):
            raise RuntimeError("Reset before reading pose")
        return self.x, self.y, self.heading

    def map_for_logging(self) -> dict[str, float]:
        """Runner metadata only; never send map details to a controller."""
        if not hasattr(self, "steps"):
            raise RuntimeError("Reset before reading map")
        return {"y_offset_m": self._map_y_offset,
                "goal_x_m": self.config["goal"]["x_m"], "goal_y_m": self._goal_y}

    def applied_wheel_speeds_for_logging(self) -> tuple[float, float]:
        """Episode logger only; absent from the controller observation/info."""
        if not hasattr(self, "_last_applied_wheel_speeds"):
            raise RuntimeError("Step before reading applied wheel speeds")
        return self._last_applied_wheel_speeds
