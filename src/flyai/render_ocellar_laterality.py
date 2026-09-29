"""Render the exploratory side-resolved ocellar audit as an SVG preview."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape


COLORS = {"left": "#ff5da9", "right": "#36d6f2", "center": "#ffc96b"}


def render(report: dict) -> str:
    if report["threshold"] != 5 or len(report["outputs"]) != 6:
        raise ValueError("Expected six output rows at exploratory threshold five")
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="760" viewBox="0 0 1280 760">',
        '<rect width="1280" height="760" fill="#111a2d"/>',
        '<text x="66" y="66" fill="#f1f7ff" font-family="Segoe UI,Arial" font-size="35" font-weight="700">Which side reaches each candidate output?</text>',
        '<text x="66" y="103" fill="#afc2d7" font-family="Segoe UI,Arial" font-size="19">Publication-time FAFB v783 · unique photoreceptor IDs · exploratory pair threshold 5</text>',
        '<circle cx="78" cy="148" r="9" fill="#ff5da9"/><text x="98" y="155" fill="#e3eaf3" font-family="Segoe UI,Arial" font-size="17">left</text>',
        '<circle cx="178" cy="148" r="9" fill="#36d6f2"/><text x="198" y="155" fill="#e3eaf3" font-family="Segoe UI,Arial" font-size="17">right</text>',
        '<circle cx="288" cy="148" r="9" fill="#ffc96b"/><text x="308" y="155" fill="#e3eaf3" font-family="Segoe UI,Arial" font-size="17">center</text>',
        '<text x="923" y="155" fill="#afc2d7" font-family="Segoe UI,Arial" font-size="17">fully same-side chain</text>',
    ]
    width_scale = 7.15
    for index, row in enumerate(report["outputs"]):
        y = 200 + index * 71
        role = row["role"]
        direct = role == "DNp28"
        counts = row["direct_photoreceptors_by_side"] if direct else row["two_hop_photoreceptors_by_side"]
        total = sum(counts.values())
        if not direct and total != row["two_hop_unique_total"]:
            raise ValueError("Side totals disagree with unique two-hop total")
        label = escape(f"{role} {row['side']}")
        lines.extend([
            f'<rect x="66" y="{y-29}" width="1148" height="57" rx="10" fill="#1b2a40"/>',
            f'<text x="85" y="{y+6}" fill="#f1f7ff" font-family="Segoe UI,Arial" font-size="19" font-weight="600">{label}</text>',
            f'<text x="263" y="{y+6}" fill="#afc2d7" font-family="Segoe UI,Arial" font-size="15">{"direct" if direct else "via OCG01"}</text>',
        ])
        left = 402.0
        for side in ("left", "right", "center"):
            width = counts[side] * width_scale
            if width:
                lines.append(f'<rect x="{left:.1f}" y="{y-12}" width="{width:.1f}" height="25" fill="{COLORS[side]}"/>')
            left += width
        lines.append(f'<text x="{min(left+10, 970):.1f}" y="{y+7}" fill="#f1f7ff" font-family="Segoe UI,Arial" font-size="18">{total}</text>')
        same_side = counts[row["side"]] if direct else row["full_ipsilateral_two_hop_photoreceptors"]
        lines.append(f'<text x="1018" y="{y+7}" fill="#f1f7ff" font-family="Segoe UI,Arial" font-size="20" font-weight="700">{same_side}/{total}</text>')
    lines.extend([
        '<rect x="66" y="637" width="1148" height="91" rx="15" fill="#30414d"/>',
        '<text x="88" y="669" fill="#ffffff" font-family="Segoe UI,Arial" font-size="19" font-weight="700">Anatomical inputs, not steering commands</text>',
        '<text x="88" y="697" fill="#d8e4ed" font-family="Segoe UI,Arial" font-size="17">Two-hop totals mix sides. Right DNp28 is flagged outlier_seg. Current Codex counts differ; P1 remains open.</text>',
        '</svg>',
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    report = json.loads((root / "data/derived/ocellar_laterality_audit.json").read_text(encoding="utf-8"))
    path = root / "figures/ocellar_laterality.svg"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(render(report), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
