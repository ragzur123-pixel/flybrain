"""Render a local-data preview of the ten pending connection checks."""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path


def render(audit: dict) -> str:
    checks = audit["checks"]
    if len(checks) != 10 or audit["portal_verified"]:
        raise ValueError("Preview requires ten locally audited, portal-pending pairs")
    max_count = max(item["forward_synapses"] for item in checks)
    colors = {"OCG01": "#7dd3fc", "DNp28": "#f9a8d4",
              "DNp20": "#a7f3d0", "DNp22": "#c4b5fd"}
    sections = [(0, "PHOTORECEPTOR → OCG01"), (4, "DIRECT PHOTORECEPTOR → DNp28"),
                (6, "OCG01 → DESCENDING NEURON")]
    y = 178
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 900" role="img" '
        'aria-label="FAFB v783 local audit of ten candidate connection pairs">',
        '<rect width="1280" height="900" fill="#0b1220"/>',
        '<text x="60" y="66" fill="#f8fafc" font-size="32" font-family="Segoe UI, Arial" font-weight="700">'
        'FlyAI · connection audit preview</text>',
        '<text x="60" y="100" fill="#b7c5d8" font-size="17" font-family="Segoe UI, Arial">'
        'FAFB v783 · 10 directed candidate pairs · raw-file counts verified locally</text>',
        '<rect x="918" y="38" width="304" height="42" rx="21" fill="#3b2f16" stroke="#c58d2a"/>',
        '<text x="1070" y="65" fill="#ffcf7a" font-size="15" font-family="Segoe UI, Arial" '
        'text-anchor="middle">PORTAL CHECKS: 0 / 10</text>',
        '<text x="60" y="139" fill="#8fa3bd" font-size="14" font-family="Segoe UI, Arial">'
        'Forward bar uses pair-summed synapse count across neuropils. Reverse count is shown at right.</text>',
        '<line x1="60" y1="153" x2="1220" y2="153" stroke="#334155"/>',
    ]
    for index, item in enumerate(checks):
        if any(index == first for first, _ in sections):
            heading = next(title for first, title in sections if first == index)
            parts.append(f'<text x="60" y="{y}" fill="#91a7c3" font-size="13" '
                         f'font-family="Segoe UI, Arial" font-weight="700">{heading}</text>')
            y += 21
        side = {"left": "L", "right": "R", "center": "C"}
        label = (f'{side[item["pre_side"]]} {item["pre_role"]}  →  '
                 f'{side[item["post_side"]]} {item["post_role"]}')
        color = colors[item["post_role"]]
        bar = round(490 * item["forward_synapses"] / max_count, 1)
        parts.extend([
            f'<text x="60" y="{y + 17}" fill="#e2e8f0" font-size="16" '
            f'font-family="Segoe UI, Arial">{escape(label)}</text>',
            f'<rect x="460" y="{y}" width="490" height="21" rx="5" fill="#1e293b"/>',
            f'<rect x="460" y="{y}" width="{bar}" height="21" rx="5" fill="{color}"/>',
            f'<text x="970" y="{y + 17}" fill="#f8fafc" font-size="18" '
            f'font-family="Segoe UI, Arial" font-weight="700">{item["forward_synapses"]}</text>',
            f'<text x="1060" y="{y + 17}" fill="#94a3b8" font-size="14" '
            f'font-family="Segoe UI, Arial">reverse {item["reverse_synapses"]}</text>',
        ])
        y += 51
    parts.extend([
        '<line x1="60" y1="815" x2="1220" y2="815" stroke="#334155"/>',
        '<text x="60" y="842" fill="#ffcf7a" font-size="15" font-family="Segoe UI, Arial">'
        'Right DNp28 carries an annotation segmentation flag; inspect before using it as a paired output.</text>',
        '<text x="60" y="868" fill="#94a3b8" font-size="14" font-family="Segoe UI, Arial">'
        'Anatomical synapse counts are not measured signal strength. Independent FlyWire/Codex review remains pending.</text>',
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    audit = json.loads((root / "data/derived/manual_pair_raw_audit.json").read_text(encoding="utf-8"))
    output = root / "figures/manual_pair_audit.svg"
    output.write_text(render(audit), encoding="utf-8")
    print(json.dumps({"output": str(output), "pairs": len(audit["checks"]),
                      "portal_verified": audit["portal_verified"]}))


if __name__ == "__main__":
    main()
