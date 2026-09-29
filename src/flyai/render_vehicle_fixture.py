"""Render a deterministic P3 software fixture, never a neural-controller result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

if not __package__:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.vehicle_env import VirtualVehicle


def simulate(config_path: Path, scenario: str) -> dict:
    env = VirtualVehicle.from_file(config_path)
    env.reset(1, scenario, start_pose=(2.0, 5.0, 0.0))
    poses = [env.pose_for_logging()]
    while True:
        _, _, terminal, truncated, info = env.step((0.7, 0.7))
        poses.append(env.pose_for_logging())
        if terminal or truncated:
            return {"scenario": scenario, "seed": 1, "commanded_wheel_speeds_m_s": [0.7, 0.7],
                    "start_pose": [2.0, 5.0, 0.0], "steps": env.steps,
                    "status": info["status"], "poses": poses}


def render(config: dict, results: list[dict]) -> str:
    scale, x0, y0 = 60, 100, 725
    point = lambda x, y: f"{x0 + x * scale:.1f},{y0 - y * scale:.1f}"
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="820" viewBox="0 0 1280 820">',
        '<rect width="1280" height="820" fill="#101827"/>',
        '<text x="72" y="63" fill="#f1f5fb" font-family="Segoe UI,Arial" font-size="32" font-weight="700">2D vehicle environment · deterministic fixture</text>',
        '<text x="73" y="93" fill="#aebed1" font-family="Segoe UI,Arial" font-size="18">Same fixed wheel command in D0 and D4 · no neural controller or learning</text>',
        f'<rect x="{x0}" y="{y0-scale*config["world"]["height_m"]}" width="{scale*config["world"]["width_m"]}" height="{scale*config["world"]["height_m"]}" fill="#19263a" stroke="#8b9bb2" stroke-width="3"/>',
    ]
    for obstacle in config["world"]["obstacles"]:
        parts.append(f'<rect x="{x0+scale*obstacle["x_min"]}" y="{y0-scale*obstacle["y_max"]}" width="{scale*(obstacle["x_max"]-obstacle["x_min"])}" height="{scale*(obstacle["y_max"]-obstacle["y_min"])}" fill="#536171"/>')
    goal = config["goal"]
    gx, gy = point(goal["x_m"], goal["y_m"]).split(",")
    parts.append(f'<circle cx="{gx}" cy="{gy}" r="{goal["radius_m"]*scale}" fill="#d8b956" fill-opacity="0.25" stroke="#f1d071" stroke-width="3"/>')
    parts.append(f'<circle cx="{gx}" cy="{gy}" r="5" fill="#f1d071"/>')
    colors = {"D0": "#26c7cb", "D4": "#ed75b6"}
    for result in results:
        points = " ".join(point(x, y) for x, y, _ in result["poses"])
        parts.append(f'<polyline points="{points}" fill="none" stroke="{colors[result["scenario"]]}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
        end_x, end_y, _ = result["poses"][-1]
        ex, ey = point(end_x, end_y).split(",")
        parts.append(f'<circle cx="{ex}" cy="{ey}" r="8" fill="{colors[result["scenario"]]}" stroke="#101827" stroke-width="2"/>')
    start_x, start_y = point(2, 5).split(",")
    parts.append(f'<circle cx="{start_x}" cy="{start_y}" r="8" fill="#f1f5fb"/>')
    parts += [
        '<text x="755" y="160" fill="#f1f5fb" font-family="Segoe UI,Arial" font-size="25" font-weight="700">Fixed-command comparison</text>',
        '<text x="755" y="206" fill="#aebed1" font-family="Segoe UI,Arial" font-size="18">Action: left = right = 0.7 m/s</text>',
        '<text x="755" y="238" fill="#aebed1" font-family="Segoe UI,Arial" font-size="18">Perturbation onset: step 20 (2 s)</text>',
    ]
    for i, result in enumerate(results):
        y = 302 + 124*i
        color = colors[result["scenario"]]
        parts.append(f'<circle cx="770" cy="{y}" r="8" fill="{color}"/>')
        parts.append(f'<text x="791" y="{y+7}" fill="#f1f5fb" font-family="Segoe UI,Arial" font-size="23" font-weight="700">{result["scenario"]}: {result["status"]}</text>')
        parts.append(f'<text x="791" y="{y+38}" fill="#aebed1" font-family="Segoe UI,Arial" font-size="18">{result["steps"]} steps · {result["steps"]*config["dt_s"]:.1f} s</text>')
    parts += [
        '<text x="755" y="625" fill="#dce6f3" font-family="Segoe UI,Arial" font-size="17">Gray: fixed obstacle · gold: virtual goal/light</text>',
        '<text x="755" y="657" fill="#aebed1" font-family="Segoe UI,Arial" font-size="17">D4 scales the right motor to 0.5 after onset.</text>',
        '<text x="73" y="784" fill="#aebed1" font-family="Segoe UI,Arial" font-size="17">Software mechanics preview only. These paths do not measure connectome behavior or task adequacy.</text>',
        '</svg>',
    ]
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--verify-existing", action="store_true",
                        help="Recompute and compare saved trace and SVG without changing them")
    args = parser.parse_args()
    root = args.workspace.resolve()
    config_path = root / ("configs/environment_fixture_2026-09-28.yaml"
                          if args.verify_existing else "configs/environment_v1.yaml")
    report_path = root / "data/derived/environment_fixture_trace.json"
    svg_path = root / "figures/environment_fixture.svg"
    if not args.verify_existing and (report_path.exists() or svg_path.exists()):
        raise FileExistsError("Environment fixture outputs already exist")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    results = [simulate(config_path, scenario) for scenario in ("D0", "D4")]
    report = {"status": "software fixture; no neural controller", "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
              "runs": results}
    products = {report_path: json.dumps(report, indent=2),
                svg_path: render(config, results)}
    if args.verify_existing:
        for path, expected in products.items():
            if path.read_text(encoding="utf-8") != expected:
                raise ValueError(f"Saved fixture differs from recomputation: {path}")
    else:
        for path, contents in products.items():
            with path.open("x", encoding="utf-8") as stream:
                stream.write(contents)
    print(json.dumps({"svg": str(svg_path), "trace": str(report_path),
                      "outcomes": [(row["scenario"], row["status"], row["steps"]) for row in results],
                      "verified_existing": args.verify_existing}))


if __name__ == "__main__":
    main()
