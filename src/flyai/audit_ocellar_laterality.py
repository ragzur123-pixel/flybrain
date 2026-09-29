"""Audit side composition of exploratory ocellar paths from a saved screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


SIDES = ("left", "right", "center")
OUTPUT_ROLES = {"DNp20", "DNp22", "DNp28"}


def analyze(screen: dict, threshold: int) -> list[dict]:
    """Count unique inputs, preserving photo and intermediate laterality."""
    if threshold < 1:
        raise ValueError("Threshold must be positive")
    edges = {}
    outputs = {}
    for edge in screen["candidate_pairs"]:
        pair = (edge["pre_root_id"], edge["post_root_id"])
        if pair in edges:
            raise ValueError(f"Duplicate directed pair: {pair}")
        if edge["pre_side"] not in SIDES or edge["post_side"] not in SIDES:
            raise ValueError(f"Unexpected side on pair: {pair}")
        if edge["pair_synapses"] < 1:
            raise ValueError(f"Nonpositive synapse count: {pair}")
        if edge["post_role"] in OUTPUT_ROLES:
            label = (edge["post_role"], edge["post_side"])
            if edge["post_root_id"] in outputs and outputs[edge["post_root_id"]] != label:
                raise ValueError(f"Conflicting output label: {edge['post_root_id']}")
            outputs[edge["post_root_id"]] = label
        edges[pair] = edge

    eligible = [edge for edge in edges.values() if edge["pair_synapses"] >= threshold]
    incoming = defaultdict(list)
    for edge in eligible:
        incoming[edge["post_root_id"]].append(edge)

    result = []
    for output_id, (role, side) in sorted(outputs.items()):
        direct = [e for e in incoming[output_id] if e["pre_role"] == "photoreceptor"]
        ocg_inputs = [e for e in incoming[output_id] if e["pre_role"] == "OCG01"]
        two_hop = defaultdict(set)
        full_ipsilateral = set()
        for ocg_edge in ocg_inputs:
            for photo_edge in incoming[ocg_edge["pre_root_id"]]:
                if photo_edge["pre_role"] != "photoreceptor":
                    continue
                photo_id = photo_edge["pre_root_id"]
                two_hop[photo_edge["pre_side"]].add(photo_id)
                if ocg_edge["pre_side"] == side and photo_edge["pre_side"] == side:
                    full_ipsilateral.add(photo_id)
        record = {
            "output_root_id": output_id, "role": role, "side": side,
            "direct_photoreceptors_by_side": {
                s: len({e["pre_root_id"] for e in direct if e["pre_side"] == s}) for s in SIDES
            },
            "ocg_inputs_by_side": {
                s: len({e["pre_root_id"] for e in ocg_inputs if e["pre_side"] == s}) for s in SIDES
            },
            "two_hop_photoreceptors_by_side": {s: len(two_hop[s]) for s in SIDES},
            "two_hop_unique_total": len(set().union(*two_hop.values())),
            "full_ipsilateral_two_hop_photoreceptors": len(full_ipsilateral),
        }
        old = next((p for p in screen["two_hop_paths_by_pair_summed_synapse_threshold"][str(threshold)]
                    if p["output_root_id"] == output_id), None)
        if old is None or (record["two_hop_unique_total"] != old["two_hop_photoreceptors"]
                           or sum(record["direct_photoreceptors_by_side"].values()) != old["direct_photoreceptors"]
                           or sum(record["ocg_inputs_by_side"].values()) != old["direct_ocg_inputs"]):
            raise ValueError(f"Recount disagrees with saved screen for output {output_id}")
        result.append(record)
    return result


def render(rows: list[dict], source_sha: str, threshold: int) -> str:
    lines = [
        "# Exploratory ocellar laterality audit",
        "",
        "This recount uses the saved publication-time v783 candidate-pair screen; it",
        "does **not** independently rescan the raw graph or resolve the current Codex",
        "count mismatch. No circuit, synapse threshold, or motor decoder is selected.",
        f"Input JSON SHA-256: `{source_sha}`. Pair-summed exploratory threshold: `{threshold}`.",
        "Counts are unique annotated photoreceptor or OCG01 root IDs, not synapses.",
        "",
        "| Output | Direct photos L/R/C | OCG inputs L/R/C | Two-hop photos L/R/C | All two-hop photos | Fully same-side two-hop photos |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        def triple(key: str) -> str:
            return "/".join(str(row[key][s]) for s in SIDES)
        lines.append(f"| {row['role']} {row['side']} | {triple('direct_photoreceptors_by_side')} | "
                     f"{triple('ocg_inputs_by_side')} | {triple('two_hop_photoreceptors_by_side')} | "
                     f"{row['two_hop_unique_total']} | {row['full_ipsilateral_two_hop_photoreceptors']} |")
    lines.extend([
        "",
        "L/R/C means biological left/right/center annotation, not image x coordinate.",
        "A fully same-side chain has both the photoreceptor and OCG01 on the",
        "output's annotated side. A photoreceptor can reach an output through",
        "more than one OCG01, so side counts describe unique photoreceptor IDs",
        "rather than distinct paths. Contralateral and center inputs are retained",
        "in the all-side counts; they cannot be interpreted as an ipsilateral",
        "sensor channel. Revisit the input encoding and output decoder before",
        "calling this a left/right steering circuit. Anatomical side does not",
        "establish excitation sign or a turning direction.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--threshold", type=int, default=5)
    args = parser.parse_args()
    root = args.workspace.resolve()
    source = root / "data/derived/ocellar_path_screen.json"
    raw = source.read_bytes()
    screen = json.loads(raw)
    rows = analyze(screen, args.threshold)
    report = {"exploratory": True, "source_screen_sha256": hashlib.sha256(raw).hexdigest(),
              "threshold": args.threshold, "outputs": rows}
    derived = root / "data/derived/ocellar_laterality_audit.json"
    document = root / "docs/ocellar_laterality_audit.md"
    if derived.exists() or document.exists():
        raise FileExistsError("Laterality audit already exists; preserve the prior result")
    derived.write_text(json.dumps(report, indent=2), encoding="utf-8")
    document.write_text(render(rows, report["source_screen_sha256"], args.threshold), encoding="utf-8")
    print(json.dumps({"outputs": len(rows), "threshold": args.threshold,
                      "derived": str(derived), "document": str(document)}))


if __name__ == "__main__":
    main()
