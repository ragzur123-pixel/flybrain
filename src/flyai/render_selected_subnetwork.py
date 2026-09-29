"""Draw a deterministic schematic of the selected anatomical edge CSV."""

from __future__ import annotations

import argparse
import csv
import html
import json
from collections import defaultdict
from pathlib import Path


COLORS = {"left": "#ff59b0", "right": "#45d6f5", "center": "#e8bd66"}


def render(nodes: list[dict], edges: list[dict], report: dict) -> str:
    if len(nodes) != report["node_count"] or len(edges) != report["directed_edge_count"]:
        raise ValueError("Node/edge CSV sizes disagree with extraction report")
    by_id = {row["root_id"]: row for row in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("Duplicate node ID")
    columns = defaultdict(list)
    for row in nodes:
        role = row["role"]
        col = "photo" if role == "photoreceptor" else "ocg" if role == "OCG01" else "output"
        if row["side"] not in COLORS:
            raise ValueError("Unexpected node side")
        columns[(col, row["side"])].append(row)
    x_by_col = {"photo": 290, "ocg": 820, "output": 1330}
    y_ranges = {"left": (220, 360), "center": (415, 555), "right": (615, 755)}
    positions = {}
    for (col, side), group in columns.items():
        group.sort(key=lambda row: int(row["root_id"]))
        low, high = y_ranges[side]
        for index, row in enumerate(group):
            y = (low + high) / 2 if len(group) == 1 else low + (high-low) * index / (len(group)-1)
            positions[row["root_id"]] = (x_by_col[col], y)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">',
        '<rect width="1600" height="900" fill="#101a2b"/>',
        '<text x="74" y="71" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="38" font-weight="700">Selected v783 anatomical subnetwork</text>',
        '<text x="74" y="113" fill="#b8c8da" font-family="Segoe UI,Arial" font-size="20">DNp20 + DNp22 family · 2024 archive · pair minimum 5 · schematic layout</text>',
        f'<text x="74" y="155" fill="#cfe0ed" font-family="Segoe UI,Arial" font-size="21">{len(nodes)} neurons    {len(edges)} directed connections    {report["pair_synapses"]:,} pair-summed synapses</text>',
    ]
    for side, x in (("left", 75), ("center", 230), ("right", 410)):
        parts.append(f'<circle cx="{x}" cy="816" r="8" fill="{COLORS[side]}"/>')
        parts.append(f'<text x="{x+17}" y="823" fill="#d4e2ef" font-family="Segoe UI,Arial" font-size="17">{side}</text>')
    for col, title in (("photo", "Photoreceptors"), ("ocg", "OCG01"), ("output", "Descending outputs")):
        parts.append(f'<text x="{x_by_col[col]}" y="183" text-anchor="middle" fill="#dbe9f5" font-family="Segoe UI,Arial" font-size="23" font-weight="600">{title}</text>')
    for edge in edges:
        pre, post = edge["pre_root_id"], edge["post_root_id"]
        if pre not in positions or post not in positions:
            raise ValueError("Edge references absent node")
        x1, y1 = positions[pre]
        x2, y2 = positions[post]
        if x2 <= x1:
            raise ValueError("Edge violates photoreceptor → OCG01 → output direction")
        count = int(edge["pair_synapses"])
        width = min(2.0, 0.45 + count / 180)
        parts.append(f'<path d="M{x1:.1f},{y1:.1f} C{x1+180:.1f},{y1:.1f} {x2-180:.1f},{y2:.1f} {x2:.1f},{y2:.1f}" stroke="{COLORS[by_id[pre]["side"]]}" stroke-opacity="0.25" stroke-width="{width:.2f}" fill="none"/>')
    for row in nodes:
        rid = row["root_id"]
        x, y = positions[rid]
        role = row["role"]
        radius = 7 if role == "photoreceptor" else 11 if role == "OCG01" else 15
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{COLORS[row["side"]]}" stroke="#f7fbff" stroke-width="1"><title>{html.escape(role)} {html.escape(row["side"])} · {rid}</title></circle>')
        if role not in ("photoreceptor", "OCG01"):
            parts.append(f'<text x="{x+27}" y="{y+6:.1f}" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="19" font-weight="600">{html.escape(role)} {html.escape(row["side"])}</text>')
    parts += [
        '<text x="590" y="823" fill="#b8c8da" font-family="Segoe UI,Arial" font-size="17">Curve direction: left → right. Color shows biological side, not signal sign.</text>',
        '<text x="75" y="862" fill="#9eb3c8" font-family="Segoe UI,Arial" font-size="16">Archive-derived connectivity only. Node positions are diagrammatic; motor decoding and behavior remain untested.</text>',
        '</svg>',
    ]
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    output = root / "figures/selected_subnetwork.svg"
    if output.exists():
        raise FileExistsError(output)
    with (root / "data/derived/selected_subnetwork_nodes.csv").open(encoding="utf-8", newline="") as stream:
        nodes = list(csv.DictReader(stream))
    with (root / "data/derived/selected_subnetwork_edges.csv").open(encoding="utf-8", newline="") as stream:
        edges = list(csv.DictReader(stream))
    report = json.loads((root / "data/derived/selected_subnetwork_report.json").read_text(encoding="utf-8"))
    output.write_text(render(nodes, edges, report), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
