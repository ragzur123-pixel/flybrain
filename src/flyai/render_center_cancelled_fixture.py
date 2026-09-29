"""Save a v0/v1 exploratory decoder comparison and a local SVG preview."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.center_cancelled_decoder import CenterCancelledDecoder, run_fixture
from flyai.decoder_fixture import run_fixture as run_v0_fixture
from flyai.selected_graph import load_selected_graph


def make_report(root: Path) -> dict:
    old_path = root / "data/derived/decoder_fixture_v0.json"
    old_bytes = old_path.read_bytes()
    old = json.loads(old_bytes)
    old_base = dict(old)
    old_base.pop("synthetic_step12_opponent_scores", None)
    expected_old = json.loads(json.dumps(run_v0_fixture(root)))
    if old_base != expected_old:
        raise ValueError("Historical v0 fixture differs from recomputation")
    current = run_fixture(root)
    graph = load_selected_graph(root)
    probe_config = json.loads((root / "configs/unsigned_rate_probe_v0.yaml").read_text(encoding="utf-8"))
    config = json.loads((root / "configs/decoder_fixture_v1.yaml").read_text(encoding="utf-8"))
    decoder = CenterCancelledDecoder(graph, probe_config, config)
    cue_scores = {}
    for side in ("left", "center", "right"):
        decoder.reset()
        for _ in range(config["synthetic_checks"]["unit_cue_steps"]):
            result = decoder.step({name: float(name == side)
                                   for name in ("left", "center", "right")})
        cue_scores[side] = {"raw": result["raw_score"],
                            "center_reference": result["center_score"],
                            "corrected": result["corrected_score"]}
        historical = old["synthetic_step12_opponent_scores"][side]
        if not math.isclose(historical, result["raw_score"], rel_tol=0, abs_tol=1e-12):
            raise ValueError("Historical v0 synthetic score differs from v1 raw probe")
    decoder.reset()
    varying_center = [0.0, 0.3, 1.0, 0.2, 0.9, 0.0] * 4
    max_center_residual = max(abs(decoder.step({"left": 0.0, "center": center,
                                                "right": 0.0})["corrected_score"])
                              for center in varying_center)
    with_center = CenterCancelledDecoder(graph, probe_config, config)
    no_center = CenterCancelledDecoder(graph, probe_config, config)
    switch_steps = config["synthetic_checks"]["switch_steps_each_side"]
    off_steps = config["synthetic_checks"]["cue_loss_steps"]
    schedule = [(1.0, 0.0)] * switch_steps + [(0.0, 1.0)] * switch_steps + \
        [(0.0, 0.0)] * off_steps
    mixed_discrepancies = []
    for index, (left, right) in enumerate(schedule):
        center = varying_center[index % len(varying_center)]
        actual = with_center.step({"left": left, "center": center,
                                   "right": right})["corrected_score"]
        expected = no_center.step({"left": left, "center": 0.0,
                                   "right": right})["corrected_score"]
        mixed_discrepancies.append(abs(actual - expected))
    return {
        "status": "exploratory v0/v1 software comparison; no selected model or pilot result",
        "historical_v0_trace_sha256": hashlib.sha256(old_bytes).hexdigest(),
        "v0_summary": {"termination_reason": old["termination_reason"],
                       "steps": old["steps"],
                       "path_xy": [[point["pose"][0], point["pose"][1]]
                                   for point in old["path"]]},
        "v1": current,
        "synthetic_step12_scores": cue_scores,
        "max_varying_center_only_residual": max_center_residual,
        "max_mixed_center_invariance_error": max(mixed_discrepancies),
    }


def render(report: dict) -> str:
    old = report["v0_summary"]
    current = report["v1"]
    if old["termination_reason"] != "goal" or current["scenario"] != "D0":
        raise ValueError("Comparison preview expects the recorded D0 fixtures")
    old_coords = " ".join(f"{130+x*82:.1f},{650-y*82:.1f}" for x, y in old["path_xy"])
    new_coords = " ".join(f"{130+p['pose'][0]*82:.1f},{650-p['pose'][1]*82:.1f}"
                          for p in current["path"])
    scores = report["synthetic_step12_scores"]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="850" viewBox="0 0 1400 850">',
        '<rect width="1400" height="850" fill="#101a2b"/>',
        '<text x="60" y="67" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="34" font-weight="700">Center-channel correction check</text>',
        '<text x="60" y="103" fill="#bbcadb" font-family="Segoe UI,Arial" font-size="18">Exploratory v783 rate probe · same fixed D0 software fixture · modeled wheel commands only</text>',
        '<rect x="60" y="142" width="870" height="560" rx="10" fill="#1c2a3d"/>',
        '<text x="87" y="181" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="23" font-weight="600">Virtual vehicle paths</text>',
        '<path d="M130,240 H870 M130,650 H870" stroke="#53667d" stroke-width="1"/>',
        '<circle cx="786" cy="240" r="41" fill="none" stroke="#94e797" stroke-width="3"/>',
        f'<polyline points="{old_coords}" fill="none" stroke="#ff5ab0" stroke-width="4" stroke-linejoin="round"/>',
        f'<polyline points="{new_coords}" fill="none" stroke="#48d7f3" stroke-width="4" stroke-linejoin="round"/>',
        '<circle cx="294" cy="240" r="7" fill="#ffb65d"/>',
        '<text x="749" y="187" fill="#d5f5d8" font-family="Segoe UI,Arial" font-size="17">goal</text>',
        '<path d="M90,588 H125" stroke="#ff5ab0" stroke-width="5"/>',
        '<text x="137" y="594" fill="#e8edf4" font-family="Segoe UI,Arial" font-size="17">v0 raw readout</text>',
        '<path d="M320,588 H355" stroke="#48d7f3" stroke-width="5"/>',
        '<text x="367" y="594" fill="#e8edf4" font-family="Segoe UI,Arial" font-size="17">v1 center-cancelled readout</text>',
        f'<text x="87" y="674" fill="#d5e5f4" font-family="Segoe UI,Arial" font-size="18">Both fixed fixtures: goal at step {old["steps"]} / {current["steps"]} (v0 / v1)</text>',
        '<rect x="960" y="142" width="380" height="560" rx="10" fill="#1c2a3d"/>',
        '<text x="990" y="181" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="22" font-weight="600">12-step synthetic cues</text>',
        '<text x="990" y="212" fill="#adbed0" font-family="Segoe UI,Arial" font-size="16">Turn score: raw → corrected</text>',
    ]
    for i, side in enumerate(("left", "center", "right")):
        y = 277 + 116*i
        raw, corrected = scores[side]["raw"], scores[side]["corrected"]
        parts.extend([
            f'<text x="990" y="{y}" fill="#e4edf6" font-family="Segoe UI,Arial" font-size="19">{side}</text>',
            f'<text x="1120" y="{y}" fill="#ff8ec7" font-family="Segoe UI,Arial" font-size="19">{raw:+.3f}</text>',
            f'<text x="1200" y="{y}" fill="#bcd0df" font-family="Segoe UI,Arial" font-size="18">→</text>',
            f'<text x="1240" y="{y}" fill="#65dcf2" font-family="Segoe UI,Arial" font-size="19">{corrected:+.3f}</text>',
        ])
    parts.extend([
        '<text x="990" y="641" fill="#d3e8f5" font-family="Segoe UI,Arial" font-size="16">Center-only residual: 0</text>',
        '<text x="60" y="752" fill="#dce8f4" font-family="Segoe UI,Arial" font-size="18">Center cancellation is exact for this assumed linear software probe; it is not a biological circuit.</text>',
        '<text x="60" y="787" fill="#a9bfd2" font-family="Segoe UI,Arial" font-size="17">One fixture and synthetic cues do not establish pilot performance, learning, or a P4 gate pass.</text>',
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()
    root = args.workspace.resolve()
    report = make_report(root)
    outputs = ((root / "data/derived/decoder_fixture_v1.json",
                (json.dumps(report, indent=2) + "\n").encode("utf-8")),
               (root / "figures/decoder_fixture_v1.svg", render(report).encode("utf-8")))
    for path, content in outputs:
        if args.verify_existing:
            if not path.exists() or path.read_bytes() != content:
                raise ValueError(f"Existing center-cancelled fixture differs: {path}")
        else:
            if path.exists():
                raise FileExistsError(f"Preserve existing center-cancelled fixture: {path}")
            path.write_bytes(content)
    print(f"PASS: v0 {report['v0_summary']['termination_reason']} "
          f"{report['v0_summary']['steps']} steps; v1 "
          f"{report['v1']['termination_reason']} {report['v1']['steps']} steps; "
          f"center residual {report['max_varying_center_only_residual']:.3g}")


if __name__ == "__main__":
    main()
