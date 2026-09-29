"""Export complete exploratory v783 ocellar candidate-ID provenance."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

import numpy as np

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.validate_raw import verify_manifest


FIELDS = ("root_id", "role", "side", "status", "annotation_field",
          "cell_type", "hemibrain_type", "position_x", "position_y",
          "position_z", "proofread_member", "snapshot", "annotation_tag")


def classify(row: dict[str, str]) -> tuple[str, str] | None:
    if row["cell_type"] == "ocellar retinula cell":
        return "photoreceptor", "cell_type"
    if row["cell_type"].startswith("OCG01"):
        return "OCG01", "cell_type"
    if row["cell_type"] == "DNp22":
        return "DNp22", "cell_type"
    if row["hemibrain_type"] in ("DNp20", "DNp28"):
        return row["hemibrain_type"], "hemibrain_type"
    return None


def inventory(rows: Iterable[dict[str, str]], proofread_ids: set[int]) -> list[dict[str, str]]:
    output = []
    seen = set()
    for row in rows:
        role_field = classify(row)
        if role_field is None:
            continue
        root_id = int(row["root_id"])
        if root_id in seen:
            raise ValueError(f"Duplicate candidate root ID: {root_id}")
        seen.add(root_id)
        if root_id not in proofread_ids:
            raise ValueError(f"Candidate root ID absent from proofread array: {root_id}")
        if row["side"] not in ("left", "right", "center"):
            raise ValueError(f"Unexpected candidate side for {root_id}: {row['side']}")
        role, field = role_field
        output.append({
            "root_id": str(root_id), "role": role, "side": row["side"],
            "status": row["status"] or "(blank)", "annotation_field": field,
            "cell_type": row["cell_type"] or "(blank)",
            "hemibrain_type": row["hemibrain_type"] or "(blank)",
            "position_x": row["pos_x"], "position_y": row["pos_y"],
            "position_z": row["pos_z"], "proofread_member": "true",
            "snapshot": "FAFB v783", "annotation_tag": "v2.1.0",
        })
    return sorted(output, key=lambda item: int(item["root_id"]))


def render_summary(rows: list[dict[str, str]], annotation_sha: str,
                   proofread_sha: str) -> str:
    counts = Counter((r["role"], r["side"]) for r in rows)
    lines = [
        "# C02 full candidate-ID provenance — 2026-09-28",
        "",
        "Status: **all 291 annotation-derived candidate IDs inventoried and",
        "checked for proofread-array membership; no subnetwork selected**.",
        "The complete per-ID table is `data/derived/candidate_id_inventory.csv`.",
        "This is a local archive inventory, not functional validation or",
        "independent current-Codex reconciliation.",
        "",
        "- Dataset: publication-time 2024 FAFB v783 archive; annotation tag `v2.1.0`.",
        f"- Annotation TSV SHA-256: `{annotation_sha}`.",
        f"- Proofread-ID array SHA-256: `{proofread_sha}`.",
        "- Every CSV row records the source annotation field, exact type strings,",
        "  biological side, status, annotation position, and proofread membership.",
        "",
        "| Candidate role | Left | Right | Center | Total |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for role in ("photoreceptor", "OCG01", "DNp20", "DNp22", "DNp28"):
        values = [counts[(role, side)] for side in ("left", "right", "center")]
        lines.append(f"| {role} | {values[0]} | {values[1]} | {values[2]} | {sum(values)} |")
    flagged = [r for r in rows if r["status"] != "(blank)"]
    lines.extend([
        "",
        f"Total: **{len(rows)}** unique IDs, all in the pinned proofread array.",
        f"Nonblank status flags: **{len(flagged)}**; right DNp28",
        "`720575940640142141` is `outlier_seg`. The CSV retains that row",
        "rather than silently excluding it. A blank status is not a guarantee",
        "of accurate segmentation or functional suitability.",
        "",
        "C03 must predeclare path and threshold criteria before any vehicle",
        "score. C04 must decide whether to include or exclude the flagged",
        "cell and specify biological-side handling and deterministic tie-breaks.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    manifest = verify_manifest(root, root / "data/raw/manifest.csv", {
        "proofread_connections_783.feather", "proofread_root_ids_783.npy",
        "per_neuron_neuropil_count_pre_783.feather",
        "Supplemental_file1_neuron_annotations_v2.1.0.tsv",
    })
    annotations = root / "data/raw/Supplemental_file1_neuron_annotations_v2.1.0.tsv"
    proofread_path = root / "data/raw/proofread_root_ids_783.npy"
    proofread = set(map(int, np.load(proofread_path, mmap_mode="r", allow_pickle=False)))
    with annotations.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        required = {"root_id", "cell_type", "hemibrain_type", "side", "status",
                    "pos_x", "pos_y", "pos_z"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Annotation TSV lacks inventory fields")
        rows = inventory(reader, proofread)
    if len(rows) != 291:
        raise ValueError(f"Unexpected candidate count: {len(rows)}")
    output = root / "data/derived/candidate_id_inventory.csv"
    summary = root / "docs/candidate_id_inventory.md"
    if output.exists() or summary.exists():
        raise FileExistsError("Candidate inventory already exists; preserve prior output")
    with output.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    summary.write_text(render_summary(
        rows,
        manifest["Supplemental_file1_neuron_annotations_v2.1.0.tsv"]["sha256"],
        manifest["proofread_root_ids_783.npy"]["sha256"]), encoding="utf-8")
    print(json.dumps({"csv": str(output), "summary": str(summary),
                      "candidate_ids": len(rows), "flagged": sum(r["status"] != "(blank)" for r in rows)}))


if __name__ == "__main__":
    main()
