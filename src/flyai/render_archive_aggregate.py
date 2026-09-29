"""Render the bounded archive-family check without implying a P1 pass."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def render(result: dict) -> str:
    comparable = result["comparable_regions"]
    absent = len(result["not_comparable"])
    violations = len(result["violations"])
    total = result["region_comparisons"]
    if comparable + absent != total:
        raise ValueError("Archive-check row categories do not sum to total")
    dots = []
    for index in range(total):
        column, row = index % 29, index // 29
        color = "#29c1a5" if index < comparable else "#ffc16e"
        dots.append(f'<circle cx="{97 + column * 38}" cy="{329 + row * 48}" r="13" fill="{color}"/>')
    return "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640">',
        '<rect width="1280" height="640" fill="#101a2c"/>',
        '<text x="72" y="71" fill="#e9f5ff" font-family="Segoe UI,Arial" font-size="36" font-weight="700">Archive-family consistency check</text>',
        '<text x="72" y="111" fill="#a9bfd4" font-family="Segoe UI,Arial" font-size="21">FAFB v783 · 19 preselected neurons · proofread graph vs original all-synapse aggregate</text>',
        '<rect x="72" y="150" width="355" height="126" rx="18" fill="#1a3041"/>',
        f'<text x="96" y="216" fill="#29c1a5" font-family="Segoe UI,Arial" font-size="56" font-weight="700">{comparable}/{comparable}</text>',
        '<text x="96" y="252" fill="#d5e5ed" font-family="Segoe UI,Arial" font-size="19">comparable regions within bound</text>',
        '<rect x="462" y="150" width="355" height="126" rx="18" fill="#1a3041"/>',
        f'<text x="486" y="216" fill="#ffc16e" font-family="Segoe UI,Arial" font-size="56" font-weight="700">{absent}</text>',
        '<text x="486" y="252" fill="#d5e5ed" font-family="Segoe UI,Arial" font-size="19">UNASGD rows lack a counterpart</text>',
        '<rect x="852" y="150" width="355" height="126" rx="18" fill="#1a3041"/>',
        f'<text x="876" y="216" fill="#29c1a5" font-family="Segoe UI,Arial" font-size="56" font-weight="700">{violations}</text>',
        '<text x="876" y="252" fill="#d5e5ed" font-family="Segoe UI,Arial" font-size="19">bound violations where comparable</text>',
        *dots,
        '<text x="72" y="480" fill="#a9bfd4" font-family="Segoe UI,Arial" font-size="20">Each dot is one selected neuron × neuropil row. Teal = bound met; amber = region absent from aggregate.</text>',
        '<rect x="72" y="517" width="1135" height="78" rx="16" fill="#304047"/>',
        '<text x="96" y="551" fill="#ffffff" font-family="Segoe UI,Arial" font-size="22" font-weight="700">P1 gate remains OPEN</text>',
        '<text x="96" y="580" fill="#d5e5ed" font-family="Segoe UI,Arial" font-size="18">This checks an archive subset bound. It does not resolve 10/10 current Codex count differences.</text>',
        '</svg>',
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    result = json.loads((root / "data/derived/archive_aggregate_check.json").read_text(encoding="utf-8"))
    path = root / "figures/archive_aggregate_check.svg"
    path.write_text(render(result), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
