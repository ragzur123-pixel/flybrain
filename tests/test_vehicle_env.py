"""Behavioral invariants for the pre-freeze virtual vehicle software fixture."""

import copy
import json
import math
import unittest
from pathlib import Path

from sys import path as sys_path
sys_path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from flyai.vehicle_env import VirtualVehicle


CONFIG = Path(__file__).resolve().parents[1] / "configs/environment_v1.yaml"


def configured(**changes):
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    for section, values in changes.items():
        if isinstance(values, dict):
            config[section].update(values)
        else:
            config[section] = values
    return VirtualVehicle(config)


class VehicleEnvironmentTests(unittest.TestCase):
    def test_dynamic_cue_switch_loss_and_restore_follow_step_clock(self):
        env = configured()
        obs, info = env.reset(10000, "D0", split="pilot", start_pose=(2.0, 5.0, 0.0))
        self.assertEqual(set(info), {"step", "status"})
        initial = obs
        for _ in range(40):
            obs, *_ = env.step((0.0, 0.0))
        self.assertGreater(obs["left"], obs["right"])
        self.assertNotEqual(obs, initial)
        for _ in range(30):
            obs, *_ = env.step((0.0, 0.0))
        self.assertGreater(obs["right"], obs["left"])
        for _ in range(30):
            obs, *_ = env.step((0.0, 0.0))
        self.assertEqual(obs, {"left": 0.0, "center": 0.0, "right": 0.0})
        for _ in range(20):
            obs, *_ = env.step((0.0, 0.0))
        self.assertEqual(obs, initial)

    def test_split_seeds_and_maps_are_disjoint_and_reproducible(self):
        for split, seed in (("pilot", 10000), ("train", 20000),
                            ("validation", 30000), ("final_test", 40000)):
            first = configured()
            second = configured()
            self.assertEqual(first.reset(seed, "D0", split=split),
                             second.reset(seed, "D4", split=split))
            self.assertEqual(first.pose_for_logging(), second.pose_for_logging())
            self.assertEqual(first.map_for_logging(), second.map_for_logging())
            self.assertIn(first.map_for_logging()["y_offset_m"], (-0.5, 0.0, 0.5))
            with self.assertRaises(ValueError):
                configured().reset(seed, split="pilot" if split != "pilot" else "final_test")
        with self.assertRaises(ValueError):
            configured().reset(10000, split="unknown")

    def test_reset_clears_previous_applied_motor_log(self):
        env = configured()
        env.reset(1)
        env.step((0.4, 0.6))
        self.assertEqual(env.applied_wheel_speeds_for_logging(), (0.4, 0.6))
        env.reset(2)
        with self.assertRaises(RuntimeError):
            env.applied_wheel_speeds_for_logging()

    def test_replay_and_observation_boundary(self):
        trajectories = []
        for _ in range(2):
            env = configured()
            obs, info = env.reset(71, "D1")
            self.assertEqual(tuple(obs), ("left", "center", "right"))
            self.assertEqual(set(info), {"step", "status"})
            trace = [(obs, env.pose_for_logging())]
            for _ in range(28):
                obs, reward, terminal, timeout, info = env.step((0.5, 0.6))
                trace.append((obs, reward, terminal, timeout, info, env.pose_for_logging()))
            trajectories.append(trace)
        self.assertEqual(trajectories[0], trajectories[1])
        self.assertTrue(all(set(item[0]) == {"left", "center", "right"} for item in trajectories[0]))
        self.assertNotEqual(trajectories[0][0][0], trajectories[0][23][0])

    def test_mirror_cue_channels_and_swap(self):
        clean = configured()
        left, _ = clean.reset(1, "D0", start_pose=(2.0, 5.0, 0.3))
        right, _ = clean.reset(1, "D0", start_pose=(2.0, 5.0, -0.3))
        self.assertAlmostEqual(left["left"], right["right"])
        self.assertAlmostEqual(left["right"], right["left"])
        swapped = configured(perturbations={"onset_step": 0})
        obs, _ = swapped.reset(1, "D3", start_pose=(2.0, 5.0, 0.3))
        self.assertAlmostEqual(obs["left"], left["right"])
        self.assertAlmostEqual(obs["right"], left["left"])

    def test_each_perturbation_only_changes_declared_channel_or_motor(self):
        baseline = configured(perturbations={"onset_step": 0})
        b, _ = baseline.reset(3, "D0", start_pose=(2.0, 5.0, 0.3))
        lost = configured(perturbations={"onset_step": 0})
        d2, _ = lost.reset(3, "D2", start_pose=(2.0, 5.0, 0.3))
        self.assertEqual(d2["left"], 0)
        self.assertEqual(d2["center"], b["center"])
        self.assertEqual(d2["right"], b["right"])
        changed_motor = configured(perturbations={"onset_step": 0})
        d4, _ = changed_motor.reset(3, "D4", start_pose=(2.0, 5.0, 0.3))
        self.assertEqual(d4, b)
        baseline.step((0.6, 0.8))
        _, _, _, _, info = changed_motor.step((0.6, 0.8))
        self.assertEqual(set(info), {"step", "status"})
        self.assertEqual(changed_motor.applied_wheel_speeds_for_logging(), (0.6, 0.4))
        self.assertNotEqual(changed_motor.pose_for_logging(), baseline.pose_for_logging())

    def test_perturbations_share_clean_prefix_and_noise_has_independent_seed(self):
        envs = {scenario: configured() for scenario in ("D0", "D1", "D2", "D3", "D4")}
        first = {scenario: env.reset(19, scenario)[0] for scenario, env in envs.items()}
        self.assertTrue(all(obs == first["D0"] for obs in first.values()))
        for _ in range(19):
            observations = {scenario: env.step((0.5, 0.6))[0] for scenario, env in envs.items()}
            self.assertTrue(all(obs == observations["D0"] for obs in observations.values()))
            self.assertTrue(all(env.pose_for_logging() == envs["D0"].pose_for_logging()
                                for env in envs.values()))
        observations = {scenario: env.step((0.5, 0.6))[0] for scenario, env in envs.items()}
        self.assertNotEqual(observations["D1"], observations["D0"])
        self.assertEqual(observations["D2"]["left"], 0.0)
        self.assertAlmostEqual(observations["D3"]["left"], observations["D0"]["right"])
        self.assertEqual(observations["D4"], observations["D0"])
        self.assertTrue(all(env.pose_for_logging() == envs["D0"].pose_for_logging()
                            for env in envs.values()))
        envs["D0"].step((0.5, 0.6))
        envs["D4"].step((0.5, 0.6))
        self.assertNotEqual(envs["D4"].pose_for_logging(), envs["D0"].pose_for_logging())

    def test_motion_clipping_goal_collision_and_timeout(self):
        env = configured()
        env.reset(2, start_pose=(2.0, 5.0, 0.0))
        env.step((-9.0, 9.0))
        self.assertAlmostEqual(env.pose_for_logging()[0], 2.05)
        self.assertAlmostEqual(env.pose_for_logging()[2], 0.25)
        with self.assertRaises(ValueError):
            env.step((math.nan, 0.5))

        goal = configured()
        goal.reset(2, start_pose=(7.5, 5.0, 0.0))
        _, _, terminal, truncated, info = goal.step((0.5, 0.5))
        self.assertTrue(terminal)
        self.assertFalse(truncated)
        self.assertEqual(info["status"], "goal")
        with self.assertRaises(RuntimeError):
            goal.step((0.0, 0.0))

        wall = configured()
        wall.reset(2, start_pose=(9.8, 5.0, 0.0))
        _, _, terminal, truncated, info = wall.step((1.0, 1.0))
        self.assertTrue(terminal)
        self.assertFalse(truncated)
        self.assertEqual(info["status"], "collision")

        obstacle = configured()
        obstacle.reset(2, start_pose=(4.0, 7.5, 0.0))
        for _ in range(10):
            _, _, terminal, _, info = obstacle.step((1.0, 1.0))
            if terminal:
                break
        self.assertEqual(info["status"], "collision")

        timer = configured(max_steps=1)
        timer.reset(2, start_pose=(2.0, 5.0, 0.0))
        _, _, terminal, truncated, info = timer.step((0.0, 0.0))
        self.assertFalse(terminal)
        self.assertTrue(truncated)
        self.assertEqual(info["status"], "timeout")

    def test_config_and_reset_reject_invalid_inputs(self):
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        bad = copy.deepcopy(config)
        bad["sensors"]["order"] = ["right", "center", "left"]
        with self.assertRaises(ValueError):
            VirtualVehicle(bad)
        overlap = copy.deepcopy(config)
        overlap["episode_design"]["split_seed_ranges_inclusive"]["final_test"] = [10050, 10100]
        with self.assertRaises(ValueError):
            VirtualVehicle(overlap)
        empty_maps = copy.deepcopy(config)
        empty_maps["episode_design"]["map_y_offsets_m"] = []
        with self.assertRaises(ValueError):
            VirtualVehicle(empty_maps)
        env = VirtualVehicle(config)
        with self.assertRaises(ValueError):
            env.reset(1, "D5")
        with self.assertRaises(ValueError):
            env.reset(1, "D0", start_pose=(0.01, 5.0, 0.0))


if __name__ == "__main__":
    unittest.main()
