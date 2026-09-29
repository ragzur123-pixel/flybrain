"""Audit selected v783 annotation transmitter predictions before sign choice."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.compare_circuit_options import PRODUCTS
from flyai.validate_raw import verify_manifest


FIELDS = ("root_id", "role", "side", "top_nt", "top_nt_conf", "known_nt",
          "known_nt_source")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--verify-existing", action="store_true",
                        help="Recompute and compare all saved audit bytes without changing them")
    args = parser.parse_args()
    root = args.workspace.resolve()
    output = root / "data/derived/selected_neurotransmitter_audit.csv"
    report_path = root / "data/derived/selected_neurotransmitter_audit.json"
    document = root / "docs/selected_neurotransmitter_audit.md"
    if not args.verify_existing and any(path.exists() for path in (output, report_path, document)):
        raise FileExistsError("Selected transmitter audit already exists")
    selection = json.loads((root / "data/derived/selected_subnetwork_report.json").read_text(encoding="utf-8"))
    nodes_path = root / "data/derived/selected_subnetwork_nodes.csv"
    edges_path = root / "data/derived/selected_subnetwork_edges.csv"
    if (hashlib.sha256(nodes_path.read_bytes()).hexdigest() != selection["nodes_csv_sha256"] or
            hashlib.sha256(edges_path.read_bytes()).hexdigest() != selection["edges_csv_sha256"]):
        raise ValueError("Selected graph CSV hash changed")
    with nodes_path.open(encoding="utf-8", newline="") as stream:
        nodes = {row["root_id"]: row for row in csv.DictReader(stream)}
    with edges_path.open(encoding="utf-8", newline="") as stream:
        edges = list(csv.DictReader(stream))
    if len(nodes) != selection["node_count"] or len(edges) != selection["directed_edge_count"]:
        raise ValueError("Selected graph size changed")
    manifest = verify_manifest(root, root / "data/raw/manifest.csv", PRODUCTS)
    annotation = root / "data/raw/Supplemental_file1_neuron_annotations_v2.1.0.tsv"
    matches = {}
    with annotation.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            rid = row["root_id"]
            if rid not in nodes:
                continue
            if rid in matches:
                raise ValueError(f"Duplicate selected annotation: {rid}")
            if row["side"] != nodes[rid]["side"]:
                raise ValueError(f"Selected side changed: {rid}")
            confidence = float(row["top_nt_conf"])
            if not 0 <= confidence <= 1:
                raise ValueError(f"Invalid top_nt_conf: {rid}")
            matches[rid] = {"root_id": rid, "role": nodes[rid]["role"],
                            "side": row["side"], "top_nt": row["top_nt"] or "(blank)",
                            "top_nt_conf": row["top_nt_conf"],
                            "known_nt": row["known_nt"] or "(blank)",
                            "known_nt_source": row["known_nt_source"] or "(blank)"}
    if set(matches) != set(nodes):
        raise ValueError("Selected IDs missing from pinned annotation TSV")
    rows = [matches[rid] for rid in sorted(matches, key=int)]
    nt_counts = Counter(row["top_nt"] for row in rows)
    role_nt = defaultdict(Counter)
    for row in rows:
        role_nt[row["role"]][row["top_nt"]] += 1
    outgoing_edges = Counter()
    outgoing_synapses = Counter()
    for edge in edges:
        nt = matches[edge["pre_root_id"]]["top_nt"]
        outgoing_edges[nt] += 1
        outgoing_synapses[nt] += int(edge["pair_synapses"])
    known_count = sum(row["known_nt"] != "(blank)" for row in rows)
    confidence = [float(row["top_nt_conf"]) for row in rows]
    report = {
        "status": "transmitter prediction coverage only; no model sign selected",
        "selected_nodes_sha256": selection["nodes_csv_sha256"],
        "selected_edges_sha256": selection["edges_csv_sha256"],
        "annotation_sha256": manifest["Supplemental_file1_neuron_annotations_v2.1.0.tsv"]["sha256"],
        "selected_count": len(rows),
        "top_nt_counts": dict(sorted(nt_counts.items())),
        "known_nt_nonblank": known_count,
        "role_top_nt_counts": {role: dict(sorted(counts.items())) for role, counts in sorted(role_nt.items())},
        "outgoing_edge_counts_by_top_nt": dict(sorted(outgoing_edges.items())),
        "outgoing_pair_synapses_by_top_nt": dict(sorted(outgoing_synapses.items())),
        "top_nt_conf_min": min(confidence),
        "top_nt_conf_median": statistics.median(confidence),
        "top_nt_conf_max": max(confidence),
    }
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    audit_bytes = stream.getvalue().encode("utf-8")
    report["audit_csv_sha256"] = hashlib.sha256(audit_bytes).hexdigest()
    lines = [
        "# Selected v783 neurotransmitter audit — 2026-09-28", "",
        "**Observation, not a sign assignment.** The pinned v2.1.0 annotation",
        "provides `top_nt` predictions and average `top_nt_conf` for all",
        "119 selected neurons, but no `known_nt` value for any of them.",
        "A prediction is not a confirmed transmitter or postsynaptic effect.", "",
        "| Predicted top transmitter | Selected neurons | Outgoing selected edges | Pair-summed synapses on those edges |",
        "| --- | ---: | ---: | ---: |",
    ]
    for nt in sorted(nt_counts):
        lines.append(f"| {nt} | {nt_counts[nt]} | {outgoing_edges[nt]} | {outgoing_synapses[nt]} |")
    lines += [
        "", f"`top_nt_conf` min/median/max: {min(confidence):.3f} / {statistics.median(confidence):.3f} / {max(confidence):.3f}.",
        "The full per-ID predictions, confidence, and",
        "source provenance are in `data/derived/selected_neurotransmitter_audit.csv`.",
        f"This set has {nt_counts['serotonin']} serotonin-predicted neurons and no confirmed",
        f"transmitter values. Those neurons supply {outgoing_edges['serotonin']}/{len(edges)} selected outgoing",
        "edges. Eckstein et al. report serotonin as their least reliable",
        "prediction and document sensory-neuron mispredictions (FW-070).",
        "The classifier predicts six transmitters and does not include",
        "histamine. Neither the annotation nor Shiu et al.'s simplified",
        "model verifies the identity or effect of these selected v783",
        "ocellar synapses. Any sign policy must be labeled as a model",
        "assumption, including for glutamate and serotonin.", "",
        f"Pinned annotation SHA-256: `{report['annotation_sha256']}`.",
        f"Selected node CSV SHA-256: `{report['selected_nodes_sha256']}`.",
        f"Audit CSV SHA-256: `{report['audit_csv_sha256']}`.", "",
    ]
    products = {output: audit_bytes,
                report_path: json.dumps(report, indent=2).encode("utf-8"),
                document: "\n".join(lines).encode("utf-8")}
    if args.verify_existing:
        for path, expected in products.items():
            if path.read_bytes() != expected:
                raise ValueError(f"Saved audit differs from recomputation: {path}")
    else:
        for path, contents in products.items():
            with path.open("xb") as saved:
                saved.write(contents)
    print(json.dumps({"nodes": len(rows), "known_nt": known_count,
                      "top_nt": dict(nt_counts), "outgoing_edges": dict(outgoing_edges),
                      "document": str(document), "verified_existing": args.verify_existing}))


if __name__ == "__main__":
    main()
