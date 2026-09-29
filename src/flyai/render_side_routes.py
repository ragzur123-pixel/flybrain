"""Render the verified side-route counts as an anatomy-only SVG chart."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.assess_side_routes import side_route_rows
from flyai.selected_graph import load_selected_graph


COLORS = {"left": "#ff59b0", "center": "#e8bd66", "right": "#45d6f5"}
SIDES = ("left", "center", "right")


def render(rows: list[dict]) -> str:
    if len(rows) != 4:
        raise ValueError("Expected four selected outputs")
    max_count = max(row["ordered_paths_by_input_side"][side]
                    for row in rows for side in SIDES)
    if max_count <= 0:
        raise ValueError("Cannot render empty anatomical route matrix")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="760" viewBox="0 0 1280 760">',
        '<rect width="1280" height="760" fill="#101a2b"/>',
        '<text x="65" y="70" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="36" font-weight="700">Which input sides reach each output?</text>',
        '<text x="65" y="109" fill="#b8c8da" font-family="Segoe UI,Arial" font-size="19">Selected v783 graph · ordered photoreceptor → OCG01 → output paths</text>',
    ]
    for side, x in zip(SIDES, (420, 700, 980)):
        parts.append(f'<circle cx="{x}" cy="170" r="8" fill="{COLORS[side]}"/>')
        parts.append(f'<text x="{x+20}" y="177" fill="#e0eaf4" font-family="Segoe UI,Arial" font-size="21" font-weight="600">{side} input</text>')
    for row_number, row in enumerate(rows):
        y = 225 + row_number * 108
        parts.append(f'<text x="65" y="{y+24}" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="22" font-weight="600">{row["role"]} {row["side"]}</text>')
        parts.append(f'<text x="65" y="{y+52}" fill="#9eb3c8" font-family="Segoe UI,Arial" font-size="15">fully same-side paths: {row["same_side_ordered_paths"]}</text>')
        for side, x in zip(SIDES, (420, 700, 980)):
            paths = row["ordered_paths_by_input_side"][side]
            unique = row["unique_inputs_by_side"][side]
            width = 190 * paths / max_count
            parts.append(f'<rect x="{x}" y="{y}" width="200" height="34" rx="6" fill="#243348"/>')
            parts.append(f'<rect x="{x}" y="{y}" width="{width:.2f}" height="34" rx="6" fill="{COLORS[side]}"/>')
            parts.append(f'<text x="{x+215}" y="{y+25}" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="22" font-weight="700">{paths}</text>')
            parts.append(f'<text x="{x}" y="{y+56}" fill="#9eb3c8" font-family="Segoe UI,Arial" font-size="15">{unique} unique photoreceptors</text>')
    parts += [
        '<text x="65" y="689" fill="#c8d8e8" font-family="Segoe UI,Arial" font-size="17">One photoreceptor may supply multiple paths. Colors mark anatomical input sides, not signal signs.</text>',
        '<text x="65" y="719" fill="#9eb3c8" font-family="Segoe UI,Arial" font-size="16">This is connectivity only. Neural response, steering direction, and task performance remain untested.</text>',
        '</svg>',
    ]
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()
    root = args.workspace.resolve()
    saved = json.loads((root / "data/derived/selected_side_routes.json").read_text(encoding="utf-8"))
    graph = load_selected_graph(root)
    rows = side_route_rows(graph)
    if saved["outputs"] != rows or saved["nodes_csv_sha256"] != graph.nodes_sha256 or saved["edges_csv_sha256"] != graph.edges_sha256:
        raise ValueError("Saved side-route counts differ from selected graph")
    output = root / "figures/selected_side_routes.svg"
    content = render(rows).encode("utf-8")
    if args.verify_existing:
        if not output.exists() or output.read_bytes() != content:
            raise ValueError("Existing side-route SVG mismatch")
    else:
        if output.exists():
            raise FileExistsError(output)
        output.write_bytes(content)
    print(f"PASS: side-route SVG {'unchanged' if args.verify_existing else 'written'}: {output}")


if __name__ == "__main__":
    main()
