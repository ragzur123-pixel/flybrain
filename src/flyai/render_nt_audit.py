"""Render the saved transmitter-prediction audit without inferring synaptic signs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape


COLORS = {"acetylcholine": "#25bbbc", "glutamate": "#efba55", "serotonin": "#d66bb3"}


def render(report: dict) -> str:
    if report["selected_count"] != sum(report["top_nt_counts"].values()):
        raise ValueError("Transmitter counts do not sum to selected neurons")
    if report["known_nt_nonblank"] != 0:
        raise ValueError("Figure annotation requires updating for confirmed labels")
    groups = (
        ("Selected neurons", report["top_nt_counts"]),
        ("Outgoing connections", report["outgoing_edge_counts_by_top_nt"]),
        ("Pair-summed synapses", report["outgoing_pair_synapses_by_top_nt"]),
    )
    for _, counts in groups:
        if set(counts) != set(COLORS) or not all(isinstance(n, int) and n >= 0 for n in counts.values()):
            raise ValueError("Unexpected transmitter categories or counts")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1320" height="780" viewBox="0 0 1320 780">',
        '<rect width="1320" height="780" fill="#101827"/>',
        '<text x="76" y="86" fill="#f3f6fb" font-family="Segoe UI,Arial" font-size="39" font-weight="700">Selected circuit: transmitter predictions</text>',
        '<text x="78" y="125" fill="#b6c2d2" font-family="Segoe UI,Arial" font-size="20">2024 FAFB v783 · 119 neurons · 169 directed connections</text>',
    ]
    for i, (label, counts) in enumerate(groups):
        total = sum(counts.values())
        y = 218 + i * 145
        parts.append(f'<text x="78" y="{y}" fill="#edf3fa" font-family="Segoe UI,Arial" font-size="23" font-weight="600">{escape(label)}</text>')
        parts.append(f'<text x="1180" y="{y}" fill="#b6c2d2" font-family="Segoe UI,Arial" font-size="20" text-anchor="end">n={total:,}</text>')
        x = 78.0
        for name in ("acetylcholine", "glutamate", "serotonin"):
            count = counts[name]
            width = 1100 * count / total
            parts.append(f'<rect x="{x:.2f}" y="{y+17}" width="{width:.2f}" height="53" fill="{COLORS[name]}"/>')
            if width > 60:
                parts.append(f'<text x="{x+width/2:.2f}" y="{y+51}" fill="#101827" font-family="Segoe UI,Arial" font-size="22" font-weight="700" text-anchor="middle">{count:,}</text>')
            x += width
    for i, name in enumerate(("acetylcholine", "glutamate", "serotonin")):
        x = 80 + i * 340
        parts.append(f'<rect x="{x}" y="640" width="22" height="22" fill="{COLORS[name]}"/>')
        parts.append(f'<text x="{x+36}" y="659" fill="#edf3fa" font-family="Segoe UI,Arial" font-size="20">{name}</text>')
    parts += [
        '<rect x="75" y="690" width="1170" height="58" rx="9" fill="#253348"/>',
        '<text x="94" y="714" fill="#f3f6fb" font-family="Segoe UI,Arial" font-size="19" font-weight="700">0 / 119 confirmed transmitter labels in the pinned annotation</text>',
        '<text x="94" y="739" fill="#b6c2d2" font-family="Segoe UI,Arial" font-size="17">Predicted transmitter is not a measured synaptic sign or motor response.</text>',
        '</svg>',
    ]
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    output = root / "figures/selected_neurotransmitter_audit.svg"
    if output.exists():
        raise FileExistsError(output)
    report = json.loads((root / "data/derived/selected_neurotransmitter_audit.json").read_text(encoding="utf-8"))
    output.write_text(render(report), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
