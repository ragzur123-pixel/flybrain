"""Save and render the one exploratory rate-to-wheel software fixture."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.decoder_fixture import run_fixture
from flyai.run_unsigned_rate_probe import make_report


def render(report: dict, cue_scores: dict[str, float]) -> str:
    if report["scenario"] != "D0" or report["split"] != "fixture":
        raise ValueError("Preview requires the fixed D0 software fixture")
    if set(cue_scores) != {"left", "center", "right"}:
        raise ValueError("Preview requires the three synthetic cue scores")
    path = report["path"]
    coords = " ".join(f"{130 + p['pose'][0] * 82:.1f},{650 - p['pose'][1] * 82:.1f}"
                      for p in path)
    goal_x, goal_y = 130 + 8 * 82, 650 - 5 * 82
    start_x, start_y = 130 + 2 * 82, 650 - 5 * 82
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="850" viewBox="0 0 1400 850">',
        '<rect width="1400" height="850" fill="#101a2b"/>',
        '<text x="60" y="68" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="34" font-weight="700">Exploratory rate-to-wheel interface</text>',
        '<text x="60" y="103" fill="#bbcadb" font-family="Segoe UI,Arial" font-size="18">Selected v783 graph · assumed unsigned rates and wheel mapping · one fixed D0 software fixture</text>',
        '<rect x="60" y="142" width="870" height="560" rx="10" fill="#1c2a3d"/>',
        '<text x="86" y="181" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="23" font-weight="600">Virtual vehicle path</text>',
        '<path d="M130,240 H870 M130,650 H870" stroke="#53667d" stroke-width="1"/>',
        f'<circle cx="{goal_x}" cy="{goal_y}" r="41" fill="none" stroke="#94e797" stroke-width="3"/>',
        f'<polyline points="{coords}" fill="none" stroke="#48d7f3" stroke-width="5" stroke-linejoin="round"/>',
        f'<circle cx="{start_x}" cy="{start_y}" r="8" fill="#ffb65d"/>',
        f'<circle cx="{130 + path[-1]["pose"][0] * 82:.1f}" cy="{650 - path[-1]["pose"][1] * 82:.1f}" r="8" fill="#48d7f3"/>',
        '<text x="260" y="265" fill="#e6f1f9" font-family="Segoe UI,Arial" font-size="17">start</text>',
        '<text x="749" y="187" fill="#d5f5d8" font-family="Segoe UI,Arial" font-size="17">goal</text>',
        f'<text x="86" y="676" fill="#d5e5f4" font-family="Segoe UI,Arial" font-size="18">Fixed fixture outcome: {report["termination_reason"]} at step {report["steps"]}</text>',
        '<rect x="960" y="142" width="380" height="560" rx="10" fill="#1c2a3d"/>',
        '<text x="990" y="181" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="22" font-weight="600">Synthetic cue check</text>',
        '<text x="990" y="213" fill="#adbed0" font-family="Segoe UI,Arial" font-size="16">12 steps with one unit cue</text>',
        '<path d="M1150,274 V520" stroke="#8192a6" stroke-width="2"/>',
    ]
    for i, side in enumerate(("left", "center", "right")):
        score = cue_scores[side]
        y = 300 + 90 * i
        endpoint = 1150 + score * 510
        fill = "#ff5ab0" if score > 0 else "#4bd7f4"
        parts.extend([
            f'<text x="990" y="{y-23}" fill="#e4edf6" font-family="Segoe UI,Arial" font-size="18">{side}</text>',
            f'<path d="M1150,{y} H{endpoint:.1f}" stroke="{fill}" stroke-width="23" stroke-linecap="round"/>',
            f'<text x="1210" y="{y+37}" fill="#d7e4ef" font-family="Segoe UI,Arial" font-size="17">{score:+.3f}</text>',
        ])
    parts.extend([
        '<text x="990" y="594" fill="#f5c9d9" font-family="Segoe UI,Arial" font-size="17">Center cue still biases left.</text>',
        '<text x="60" y="752" fill="#dce8f4" font-family="Segoe UI,Arial" font-size="18">These are modeled software outputs and virtual wheel commands, not observed neuron activity or fly behavior.</text>',
        '<text x="60" y="787" fill="#a9bfd2" font-family="Segoe UI,Arial" font-size="17">No training, held-out test, pilot comparison, biological motor sign, or P4 gate claim.</text>',
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()
    root = args.workspace.resolve()
    report = run_fixture(root)
    trace = json.loads((root / "data/derived/unsigned_rate_probe_v0.json").read_text(encoding="utf-8"))
    if trace != make_report(root):
        raise ValueError("Saved synthetic cue trace differs from its pinned graph/config")
    scores = {}
    for item in trace["traces"]:
        output = item["points"][11]["outputs"]
        scores[item["stimulus"]] = (output["DNp20 left"] + output["DNp22 left"] -
                                    output["DNp20 right"] - output["DNp22 right"]) / 2
    report["synthetic_step12_opponent_scores"] = scores
    outputs = ((root / "data/derived/decoder_fixture_v0.json",
                (json.dumps(report, indent=2) + "\n").encode("utf-8")),
               (root / "figures/decoder_fixture_v0.svg", render(report, scores).encode("utf-8")))
    for path, content in outputs:
        if args.verify_existing:
            if not path.exists() or path.read_bytes() != content:
                raise ValueError(f"Existing exploratory fixture differs: {path}")
        else:
            if path.exists():
                raise FileExistsError(f"Preserve existing exploratory fixture: {path}")
            path.write_bytes(content)
    print(f"PASS: {report['termination_reason']} at step {report['steps']}; " +
          ("existing files unchanged" if args.verify_existing else "trace and SVG written"))


if __name__ == "__main__":
    main()
