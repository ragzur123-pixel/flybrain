"""Render C03 side-consistent reachability sensitivity as an SVG figure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def render(report: dict) -> str:
    primary = str(report["primary_threshold"])
    sensitivity = str(report["sensitivity_threshold"])
    by_threshold = report["by_threshold"]
    lookup = {
        threshold: {(row["role"], row["side"]): row for row in by_threshold[threshold]["outputs"]}
        for threshold in (primary, sensitivity)
    }
    order = [(role, side) for role in ("DNp20", "DNp22", "DNp28")
             for side in ("left", "right")]
    if any(set(lookup[t]) != set(order) for t in lookup):
        raise ValueError("Expected six candidate outputs at both thresholds")
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="850" viewBox="0 0 1280 850">',
        '<rect width="1280" height="850" fill="#111a2d"/>',
        '<text x="65" y="69" fill="#f1f7ff" font-family="Segoe UI,Arial" font-size="34" font-weight="700">Anatomical path sensitivity</text>',
        '<text x="65" y="106" fill="#aebfd3" font-family="Segoe UI,Arial" font-size="19">2024 FAFB v783 archive · unique photoreceptor IDs per output · no behavior tested</text>',
        '<rect x="65" y="135" width="18" height="18" fill="#32d0ad"/><text x="94" y="151" fill="#e2edf4" font-family="Segoe UI,Arial" font-size="17">fully same-side route</text>',
        '<rect x="326" y="135" width="18" height="18" fill="#657a92"/><text x="355" y="151" fill="#e2edf4" font-family="Segoe UI,Arial" font-size="17">remaining unique inputs</text>',
        '<text x="945" y="151" fill="#aebfd3" font-family="Segoe UI,Arial" font-size="17">same-side / all IDs</text>',
    ]
    scale = 2.95
    for index, key in enumerate(order):
        y = 201 + index * 93
        role, side = key
        label = f"{role} {side}" + (" *" if role == "DNp28" and side == "right" else "")
        lines.append(f'<rect x="65" y="{y-28}" width="1149" height="82" rx="11" fill="#1b2a40"/>')
        lines.append(f'<text x="83" y="{y+5}" fill="#f1f7ff" font-family="Segoe UI,Arial" font-size="19" font-weight="600">{label}</text>')
        for offset, threshold in ((-11, sensitivity), (21, primary)):
            row = lookup[threshold][key]
            total = row["unique_photoreceptors_total"]
            same = row["fully_same_side_photoreceptors"]
            if not 0 <= same <= total:
                raise ValueError(f"Invalid side subset for {key}")
            bar_y = y + offset - 11
            lines.append(f'<text x="261" y="{y+offset+5}" fill="#aebfd3" font-family="Segoe UI,Arial" font-size="16">≥{threshold}</text>')
            lines.append(f'<rect x="314" y="{bar_y}" width="{same*scale:.1f}" height="18" fill="#32d0ad"/>')
            if total > same:
                lines.append(f'<rect x="{314+same*scale:.1f}" y="{bar_y}" width="{(total-same)*scale:.1f}" height="18" fill="#657a92"/>')
            lines.append(f'<text x="945" y="{y+offset+5}" fill="#f1f7ff" font-family="Segoe UI,Arial" font-size="17" font-weight="600">{same} / {total}</text>')
    lines.extend([
        '<rect x="65" y="750" width="1149" height="75" rx="13" fill="#30414d"/>',
        '<text x="86" y="781" fill="#ffffff" font-family="Segoe UI,Arial" font-size="18" font-weight="700">All three output roles have bilateral paths at both screens.</text>',
        '<text x="86" y="807" fill="#d8e4ed" font-family="Segoe UI,Arial" font-size="16">* Right DNp28 is outlier_seg. Pair minimums 1 and 5 are analytical screens, not biological cutoffs or a selected controller.</text>',
        '</svg>',
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    report = json.loads((root / "data/derived/path_feasibility_v1.json").read_text(encoding="utf-8"))
    output = root / "figures/path_feasibility_v1.svg"
    if output.exists():
        raise FileExistsError(output)
    output.write_text(render(report), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
