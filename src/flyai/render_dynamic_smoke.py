"""Render the two exploratory moving-cue traces without pilot claims."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.dynamic_smoke import run_smoke


def render(report: dict) -> str:
    if (report["split"], report["seed"]) != ("train", 20000) or \
            [run["scenario"] for run in report["runs"]] != ["D0", "D4"]:
        raise ValueError("Preview requires the declared training-seed smoke")
    colors = ("#ff69b7", "#50d6ee")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="840" viewBox="0 0 1400 840">',
        '<rect width="1400" height="840" fill="#101a2b"/>',
        '<text x="60" y="67" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="33" font-weight="700">Moving-cue software smoke</text>',
        '<text x="60" y="103" fill="#b8cad8" font-family="Segoe UI,Arial" font-size="18">Exploratory v1 decoder · train seed 20000 · paired D0 and D4 · not a pilot result</text>',
        '<rect x="60" y="145" width="905" height="550" rx="10" fill="#1c2a3d"/>',
        '<text x="88" y="183" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="23" font-weight="600">Virtual paths on the same map</text>',
        '<path d="M120,400 H925 M120,560 H925" stroke="#42546a" stroke-width="1"/>',
        '<rect x="480" y="160" width="80" height="80" fill="#5b7083"/>',
        '<circle cx="760" cy="400" r="40" fill="none" stroke="#a6e7aa" stroke-width="3"/>',
        '<text x="730" y="345" fill="#d4f5d8" font-family="Segoe UI,Arial" font-size="17">goal</text>',
    ]
    for run, color in zip(report["runs"], colors):
        points = " ".join(f"{120+point['pose'][0]*80:.2f},{800-point['pose'][1]*80:.2f}"
                          for point in run["path"])
        last = run["path"][-1]["pose"]
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="4" stroke-linejoin="round"/>')
        parts.append(f'<circle cx="{120+last[0]*80:.2f}" cy="{800-last[1]*80:.2f}" r="7" fill="{color}"/>')
    parts.extend([
        '<circle cx="280" cy="400" r="7" fill="#ffbb63"/>',
        '<text x="255" y="430" fill="#e4eaf1" font-family="Segoe UI,Arial" font-size="17">start</text>',
        '<path d="M92,613 H127" stroke="#ff69b7" stroke-width="5"/>',
        '<text x="139" y="619" fill="#f2e7ef" font-family="Segoe UI,Arial" font-size="18">D0: collision, step 133</text>',
        '<path d="M425,613 H460" stroke="#50d6ee" stroke-width="5"/>',
        '<text x="472" y="619" fill="#e5f3f8" font-family="Segoe UI,Arial" font-size="18">D4: timeout, step 300</text>',
        '<rect x="990" y="145" width="350" height="550" rx="10" fill="#1c2a3d"/>',
        '<text x="1020" y="183" fill="#f4f8ff" font-family="Segoe UI,Arial" font-size="22" font-weight="600">Cue clock</text>',
    ])
    for index, (step, source) in enumerate(((0, "goal"), (40, "upper"), (70, "lower"),
                                            (100, "off"), (120, "goal restored"))):
        y = 255 + 75 * index
        parts.append(f'<text x="1020" y="{y}" fill="#a9bfd1" font-family="Segoe UI,Arial" font-size="18">step {step}</text>')
        parts.append(f'<text x="1140" y="{y}" fill="#e2edf5" font-family="Segoe UI,Arial" font-size="18">{source}</text>')
    parts.extend([
        '<text x="60" y="749" fill="#dce8f4" font-family="Segoe UI,Arial" font-size="18">The fixed D0 fixture succeeded earlier; this moving-cue D0 attempt did not. Controller and task remain unvalidated.</text>',
        '<text x="60" y="786" fill="#a9bfd2" font-family="Segoe UI,Arial" font-size="17">One training seed, no parameter tuning or held-out evaluation; virtual sensors, motors and outputs are modeled.</text>',
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()
    root = args.workspace.resolve()
    saved = json.loads((root / "data/derived/dynamic_smoke_v0.json").read_text(encoding="utf-8"))
    if saved != json.loads(json.dumps(run_smoke(root))):
        raise ValueError("Saved moving-cue trace differs from recomputation")
    content = render(saved).encode("utf-8")
    output = root / "figures/dynamic_smoke_v0.svg"
    if args.verify_existing:
        if not output.exists() or output.read_bytes() != content:
            raise ValueError("Existing moving-cue figure differs")
    else:
        if output.exists():
            raise FileExistsError("Preserve existing moving-cue figure")
        output.write_bytes(content)
    print("PASS: moving-cue D0/D4 paths " +
          ("verified" if args.verify_existing else "rendered"))


if __name__ == "__main__":
    main()
