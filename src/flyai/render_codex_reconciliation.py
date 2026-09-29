"""Show local archive and current Codex counts without merging the products."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def render(report: dict) -> str:
    pairs = report["pairs"]
    if len(pairs) != 10:
        raise ValueError("Expected the ten preselected manual-check pairs")
    maximum = max(max(pair["archive_synapses"], pair["codex_synapses"]) for pair in pairs)
    side = {"left": "L", "right": "R", "center": "C"}
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 900" role="img" '
        'aria-label="FAFB v783 archive versus current Codex connectivity counts">',
        '<rect width="1280" height="900" fill="#0b1220"/>',
        '<text x="60" y="65" fill="#f8fafc" font-size="32" font-family="Segoe UI, Arial" '
        'font-weight="700">FlyAI · connection workcheck</text>',
        '<text x="60" y="99" fill="#b7c5d8" font-size="17" font-family="Segoe UI, Arial">'
        'Ten preselected FAFB v783 pairs · publication archive vs current Codex CSV</text>',
        '<rect x="955" y="35" width="267" height="48" rx="24" fill="#482c1e" stroke="#f59e0b"/>',
        '<text x="1088" y="65" fill="#ffd28a" font-size="16" font-family="Segoe UI, Arial" '
        'text-anchor="middle">10 / 10 DISCREPANT</text>',
        '<rect x="60" y="119" width="16" height="16" rx="3" fill="#f9a8d4"/>',
        '<text x="84" y="133" fill="#dbeafe" font-size="14" font-family="Segoe UI, Arial">'
        'Pinned archive</text>',
        '<rect x="210" y="119" width="16" height="16" rx="3" fill="#67e8f9"/>',
        '<text x="234" y="133" fill="#dbeafe" font-size="14" font-family="Segoe UI, Arial">'
        'Current Codex export</text>',
        '<line x1="60" y1="153" x2="1220" y2="153" stroke="#334155"/>',
    ]
    for i, pair in enumerate(pairs):
        y = 176 + i * 61
        archive = pair["archive_synapses"]
        codex = pair["codex_synapses"]
        pre_role = "photo" if pair["pre_role"] == "photoreceptor" else pair["pre_role"]
        label = (f'{side[pair["pre_side"]]} {pre_role} → '
                 f'{side[pair["post_side"]]} {pair["post_role"]}')
        parts.extend([
            f'<text x="60" y="{y+22}" fill="#e2e8f0" font-size="16" '
            f'font-family="Segoe UI, Arial">{label}</text>',
            f'<rect x="370" y="{y}" width="570" height="16" rx="4" fill="#1e293b"/>',
            f'<rect x="370" y="{y}" width="{round(570*archive/maximum,1)}" height="16" '
            f'rx="4" fill="#f9a8d4"/>',
            f'<rect x="370" y="{y+21}" width="570" height="16" rx="4" fill="#1e293b"/>',
            f'<rect x="370" y="{y+21}" width="{round(570*codex/maximum,1)}" height="16" '
            f'rx="4" fill="#67e8f9"/>',
            f'<text x="964" y="{y+15}" fill="#f9a8d4" font-size="15" '
            f'font-family="Segoe UI, Arial">{archive}</text>',
            f'<text x="964" y="{y+36}" fill="#67e8f9" font-size="15" '
            f'font-family="Segoe UI, Arial">{codex}</text>',
            f'<text x="1080" y="{y+29}" fill="#ffd28a" font-size="15" '
            f'font-family="Segoe UI, Arial">+{pair["delta"]}</text>',
        ])
    parts.extend([
        '<line x1="60" y1="816" x2="1220" y2="816" stroke="#334155"/>',
        '<text x="60" y="843" fill="#ffd28a" font-size="15" font-family="Segoe UI, Arial">'
        'The IDs and directions match; the synapse counts do not. Keep the two products separate.</text>',
        '<text x="60" y="869" fill="#94a3b8" font-size="14" font-family="Segoe UI, Arial">'
        'P1 gate open · no circuit selected · Codex FAQ says current downloads may differ from publication archives.</text>',
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    report = json.loads((root / "data/derived/codex_reconciliation.json").read_text(encoding="utf-8"))
    output = root / "figures/codex_reconciliation.svg"
    output.write_text(render(report), encoding="utf-8")
    print(json.dumps({"output": str(output), "pairs": len(report["pairs"]) }))


if __name__ == "__main__":
    main()
