"""Draw the exploratory unsigned software response traces, without behavior claims."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.run_unsigned_rate_probe import make_report


COLORS = ("#ff59b0", "#45d6f5", "#f5a4d2", "#a4edfa")
LABELS = ("DNp20 left", "DNp20 right", "DNp22 left", "DNp22 right")


def render(report: dict) -> str:
    if report["output_order"] != list(LABELS) or len(report["traces"]) != 3:
        raise ValueError("Unexpected probe output order or trace count")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="940" viewBox="0 0 1400 940">',
        '<rect width="1400" height="940" fill="#101a2b"/>',
        '<text x="64" y="70" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="37" font-weight="700">Exploratory unsigned response probe</text>',
        '<text x="64" y="109" fill="#b8c8da" font-family="Segoe UI,Arial" font-size="19">Selected v783 graph · one cue side at a time · modeled rate from 0 to 1</text>',
    ]
    for index, (label, color) in enumerate(zip(LABELS, COLORS)):
        x = 65 + index * 320
        dash = ' stroke-dasharray="9 6"' if index >= 2 else ""
        parts.append(f'<path d="M{x},158 H{x+34}" stroke="{color}" stroke-width="4"{dash}/>')
        parts.append(f'<text x="{x+44}" y="164" fill="#dfeaf4" font-family="Segoe UI,Arial" font-size="18">{label}</text>')
    for panel, trace in enumerate(report["traces"]):
        top = 218 + panel * 217
        left, width, height = 260, 1050, 145
        points = trace["points"]
        total = len(points)
        if total != report["stimulus_steps"] + report["silence_steps"]:
            raise ValueError("Probe point count changed")
        parts.append(f'<text x="65" y="{top+30}" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="24" font-weight="600">{trace["stimulus"]} cue</text>')
        parts.append(f'<text x="65" y="{top+61}" fill="#9eb3c8" font-family="Segoe UI,Arial" font-size="16">{report["stimulus_steps"]} steps on, {report["silence_steps"]} off</text>')
        parts.append(f'<rect x="{left}" y="{top}" width="{width}" height="{height}" rx="7" fill="#1c2a3d"/>')
        for fraction, caption in ((0, "0"), (0.5, "0.35"), (1, "0.7")):
            y = top + height * (1 - fraction)
            parts.append(f'<path d="M{left},{y:.1f} H{left+width}" stroke="#43536a" stroke-width="1"/>')
            parts.append(f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" fill="#9eb3c8" font-family="Segoe UI,Arial" font-size="14">{caption}</text>')
        split_x = left + width * (report["stimulus_steps"] - 0.5) / (total - 1)
        parts.append(f'<path d="M{split_x:.1f},{top} V{top+height}" stroke="#dbe9f5" stroke-opacity="0.65" stroke-dasharray="5 5"/>')
        parts.append(f'<text x="{split_x+9:.1f}" y="{top-8}" fill="#dbe9f5" font-family="Segoe UI,Arial" font-size="14">cue off</text>')
        for index, (label, color) in enumerate(zip(LABELS, COLORS)):
            coords = []
            for n, point in enumerate(points):
                value = point["outputs"][label]
                if not 0 <= value <= 0.7:
                    raise ValueError("Probe value exceeds chart range")
                x = left + width * n / (total - 1)
                y = top + height * (1 - value / 0.7)
                coords.append(f"{x:.2f},{y:.2f}")
            dash = ' stroke-dasharray="9 6"' if index >= 2 else ""
            parts.append(f'<polyline points="{" ".join(coords)}" fill="none" stroke="{color}" stroke-width="3"{dash}/>')
    parts += [
        '<text x="64" y="884" fill="#c8d8e8" font-family="Segoe UI,Arial" font-size="17">Assumed count normalization and relaxation produce these software traces; they are not recorded fly-neuron activity.</text>',
        '<text x="64" y="914" fill="#9eb3c8" font-family="Segoe UI,Arial" font-size="16">No motor decoder, vehicle episode, training, or biological sign has been selected or tested.</text>',
        '</svg>',
    ]
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()
    root = args.workspace.resolve()
    saved = json.loads((root / "data/derived/unsigned_rate_probe_v0.json").read_text(encoding="utf-8"))
    if saved != make_report(root):
        raise ValueError("Saved probe trace differs from current config and graph")
    content = render(saved).encode("utf-8")
    output = root / "figures/unsigned_rate_probe_v0.svg"
    if args.verify_existing:
        if not output.exists() or output.read_bytes() != content:
            raise ValueError("Existing unsigned-rate SVG differs")
    else:
        if output.exists():
            raise FileExistsError("Preserve existing unsigned-rate SVG")
        output.write_bytes(content)
    print(f"PASS: unsigned-rate SVG {'unchanged' if args.verify_existing else 'written'}")


if __name__ == "__main__":
    main()
