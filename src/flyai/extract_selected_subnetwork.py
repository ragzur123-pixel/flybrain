"""Extract the owner-selected C04 anatomical subnetwork from verified v783 raw data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.compare_circuit_options import PRODUCTS, option_footprint
from flyai.screen_ocellar import screen
from flyai.validate_raw import verify_manifest


def weak_component_sizes(node_ids: list[str], edges: list[dict]) -> list[int]:
    adjacent = {rid: set() for rid in node_ids}
    for edge in edges:
        pre, post = edge["pre_root_id"], edge["post_root_id"]
        if pre not in adjacent or post not in adjacent:
            raise ValueError("Edge endpoint absent from selected node list")
        adjacent[pre].add(post)
        adjacent[post].add(pre)
    visited = set()
    sizes = []
    for rid in node_ids:
        if rid in visited:
            continue
        frontier = [rid]
        visited.add(rid)
        size = 0
        while frontier:
            current = frontier.pop()
            size += 1
            for neighbor in adjacent[current] - visited:
                visited.add(neighbor)
                frontier.append(neighbor)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def unreachable_to_outputs(node_ids: list[str], edges: list[dict], outputs: set[str]) -> list[str]:
    reverse = defaultdict(set)
    for edge in edges:
        reverse[edge["post_root_id"]].add(edge["pre_root_id"])
    reachable = set(outputs)
    frontier = list(outputs)
    while frontier:
        for parent in reverse[frontier.pop()] - reachable:
            reachable.add(parent)
            frontier.append(parent)
    return sorted(set(node_ids) - reachable, key=int)


def validate_config(config: dict, inventory: dict[str, dict]) -> tuple[str, ...]:
    roles = tuple(config["output_roles"])
    if roles != ("DNp20", "DNp22") or config["side_policy"] != "all_sides":
        raise ValueError("C04 chosen roles or side policy changed")
    if config["min_pair_synapses"] != 5 or config["sensitivity_min_pair_synapses"] != 1:
        raise ValueError("C04 thresholds changed")
    if config["behavior_data_used_for_selection"] is not False:
        raise ValueError("Behavior-use declaration changed")
    ids = config["output_root_ids"]
    if len(ids) != 4 or len(set(ids)) != 4:
        raise ValueError("Expected four unique selected outputs")
    for rid in ids:
        if rid not in inventory or inventory[rid]["role"] not in roles:
            raise ValueError(f"Selected output lacks candidate provenance: {rid}")
    for role in roles:
        if {inventory[rid]["side"] for rid in ids if inventory[rid]["role"] == role} != {"left", "right"}:
            raise ValueError(f"Selected role is not bilateral: {role}")
    if config["max_nodes"] < 4 or config["max_directed_edges"] < 4:
        raise ValueError("Invalid graph cap")
    return roles


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--verify-existing", action="store_true",
                        help="Rescan raw data and compare every selected CSV row without rewriting files")
    args = parser.parse_args()
    root = args.workspace.resolve()
    out_edges = root / "data/derived/selected_subnetwork_edges.csv"
    out_nodes = root / "data/derived/selected_subnetwork_nodes.csv"
    out_report = root / "data/derived/selected_subnetwork_report.json"
    out_doc = root / "docs/selected_subnetwork.md"
    if args.verify_existing and not all(path.exists() for path in (out_edges, out_nodes, out_report, out_doc)):
        raise FileNotFoundError("Verification requires the prior selected graph outputs")
    if not args.verify_existing and any(path.exists() for path in (out_edges, out_nodes, out_report, out_doc)):
        raise FileExistsError("Selected subnetwork output exists; preserve prior extraction")
    config_path = root / "configs/subnetwork_selection.yaml"
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)  # JSON is a YAML 1.2 subset.
    inventory_path = root / "data/derived/candidate_id_inventory.csv"
    inventory_bytes = inventory_path.read_bytes()
    with inventory_path.open(encoding="utf-8", newline="") as stream:
        inventory = {row["root_id"]: row for row in csv.DictReader(stream)}
    if len(inventory) != 291:
        raise ValueError("C02 candidate inventory count changed")
    roles = validate_config(config, inventory)
    c03 = json.loads((root / "data/derived/path_feasibility_v1.json").read_text(encoding="utf-8"))
    if (hashlib.sha256(inventory_bytes).hexdigest() != c03["candidate_inventory_sha256"] or
            config["min_pair_synapses"] != c03["primary_threshold"]):
        raise ValueError("C02/C03 selection inputs disagree")
    manifest = verify_manifest(root, root / "data/raw/manifest.csv", PRODUCTS)
    raw_hash = manifest["proofread_connections_783.feather"]["sha256"]
    if raw_hash != c03["raw_connection_sha256"]:
        raise ValueError("Selected raw graph differs from C03")
    labels = {int(rid): {"role": row["role"], "side": row["side"],
                         "status": row["status"]} for rid, row in inventory.items()}
    fresh = screen(root / "data/raw/proofread_connections_783.feather", labels)
    old = json.loads((root / "data/derived/ocellar_path_screen.json").read_text(encoding="utf-8"))
    if (fresh["row_count_scanned"] != c03["raw_rows_scanned"] or
            fresh["candidate_pairs"] != old["candidate_pairs"] or
            fresh["candidate_pair_count"] != c03["candidate_pairs"]):
        raise ValueError("Fresh candidate graph disagrees with C03 screen")
    candidate_pair_synapses = sum(row["pair_synapses"] for row in fresh["candidate_pairs"])
    graph = option_footprint(fresh["candidate_pairs"], inventory, roles,
                             config["min_pair_synapses"], False, include_graph=True)
    strict = option_footprint(fresh["candidate_pairs"], inventory, roles,
                              config["min_pair_synapses"], True)
    if (graph["node_count"] > config["max_nodes"] or
            graph["directed_edge_count"] > config["max_directed_edges"]):
        raise ValueError("Graph exceeds C04 caps; no truncation allowed")
    if set(config["output_root_ids"]) != {row["root_id"] for row in graph["outputs"]}:
        raise ValueError("Extracted outputs differ from selected IDs")
    if not graph["all_outputs_reachable"] or not strict["all_outputs_reachable"]:
        raise ValueError("Selected output has no required same-side path")
    if any(inventory[rid]["status"] != "(blank)" for rid in graph["node_ids"]):
        raise ValueError("Selected graph contains a nonblank-status node")
    comparison = json.loads((root / "data/derived/c04_option_footprints.json").read_text(encoding="utf-8"))
    expected = comparison["options"]["5"]["ocg_family"]["all_sides"]
    if any(graph[key] != expected[key] for key in ("node_count", "directed_edge_count", "pair_synapses", "roles", "outputs")):
        raise ValueError("Fresh extraction disagrees with C04 footprint")
    components = weak_component_sizes(graph["node_ids"], graph["edges"])
    unreachable = unreachable_to_outputs(graph["node_ids"], graph["edges"],
                                         set(config["output_root_ids"]))
    if unreachable:
        raise ValueError("Selected graph contains nodes without output path")
    if args.verify_existing:
        existing = json.loads(out_report.read_text(encoding="utf-8"))
        with out_edges.open(encoding="utf-8", newline="") as stream:
            saved_edges = list(csv.DictReader(stream))
        with out_nodes.open(encoding="utf-8", newline="") as stream:
            saved_nodes = list(csv.DictReader(stream))
        expected_edges = [{name: str(value) for name, value in row.items()}
                          for row in graph["edges"]]
        expected_nodes = [inventory[rid] for rid in graph["node_ids"]]
        if saved_edges != expected_edges or saved_nodes != expected_nodes:
            raise ValueError("Rerun selected node/edge rows differ")
        if (existing["raw_connection_sha256"] != raw_hash or
                existing["inventory_sha256"] != hashlib.sha256(inventory_bytes).hexdigest() or
                existing["config_sha256"] != hashlib.sha256(config_bytes).hexdigest() or
                existing["edges_csv_sha256"] != hashlib.sha256(out_edges.read_bytes()).hexdigest() or
                existing["nodes_csv_sha256"] != hashlib.sha256(out_nodes.read_bytes()).hexdigest() or
                existing["node_count"] != graph["node_count"] or
                existing["directed_edge_count"] != graph["directed_edge_count"] or
                existing["pair_synapses"] != graph["pair_synapses"] or
                existing["weak_component_sizes"] != components):
            raise ValueError("Rerun selected graph metadata/hash differs")
        print(json.dumps({"verified_existing": True, "nodes": graph["node_count"],
                          "edges": graph["directed_edge_count"],
                          "edge_sha256": existing["edges_csv_sha256"],
                          "node_sha256": existing["nodes_csv_sha256"]}))
        return
    code_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report = {
        "status": "anatomical extraction only; no model weights/signs or behavior",
        "dataset": config["dataset"], "annotation_tag": config["annotation_tag"],
        "raw_connection_sha256": raw_hash,
        "inventory_sha256": hashlib.sha256(inventory_bytes).hexdigest(),
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "extractor_sha256": code_hash,
        "command": ".venv\\Scripts\\python.exe src\\flyai\\extract_selected_subnetwork.py --workspace .",
        "raw_rows_scanned": fresh["row_count_scanned"],
        "candidate_node_count": fresh["candidate_id_count"],
        "candidate_pairs_scanned": fresh["candidate_pair_count"],
        "candidate_pair_synapses": candidate_pair_synapses,
        "threshold": config["min_pair_synapses"],
        "side_policy": config["side_policy"],
        "node_count": graph["node_count"],
        "directed_edge_count": graph["directed_edge_count"],
        "pair_synapses": graph["pair_synapses"],
        "role_counts": graph["roles"],
        "weak_component_sizes": components,
        "unreachable_to_any_output_count": len(unreachable),
        "unreachable_to_any_output_fraction": len(unreachable) / graph["node_count"],
        "selected_outputs": graph["outputs"],
        "fully_same_side_outputs": strict["outputs"],
        "model_weight_rule": config["model_weight_rule"],
    }
    edge_columns = ("pre_root_id", "post_root_id", "pre_role", "post_role", "pre_side", "post_side",
                    "pair_synapses", "neuropil_rows")
    with out_edges.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=edge_columns)
        writer.writeheader()
        writer.writerows({name: row[name] for name in edge_columns} for row in graph["edges"])
    with out_nodes.open("w", encoding="utf-8", newline="") as stream:
        columns = tuple(next(iter(inventory.values())).keys())
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(inventory[rid] for rid in graph["node_ids"])
    report["edges_csv_sha256"] = hashlib.sha256(out_edges.read_bytes()).hexdigest()
    report["nodes_csv_sha256"] = hashlib.sha256(out_nodes.read_bytes()).hexdigest()
    out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    out_doc.write_text(
        "# Selected v783 anatomical subnetwork — 2026-09-28\n\n"
        "Rüzgar selected the DNp20+DNp22 output family. This is a directed\n"
        "archive-derived graph only; sensor encoding, signs, model weights,\n"
        "motor decoder, and behavioral validity remain open.\n\n"
        f"- Source rows rescanned: **{report['raw_rows_scanned']:,}**. Before the role-path filter, the C02 candidate graph had **{report['candidate_node_count']}** annotated nodes, **{report['candidate_pairs_scanned']}** directed candidate pairs, and **{candidate_pair_synapses:,}** pair-summed synapses.\n"
        f"- Selected complete-path graph: **{graph['node_count']}** nodes, **{graph['directed_edge_count']}** directed edges, **{graph['pair_synapses']:,}** pair-summed synapses.\n"
        f"- Selected roles: {graph['roles']}. Weak component sizes: {components}.\n"
        f"- Nodes without a directed path to any selected output: **{len(unreachable)}**. All four outputs also have fully same-side photoreceptor paths.\n"
        "- The graph retains all biological left/right/center paths that satisfy the two-edge rule; biological side is metadata, not a motor command.\n"
        f"- Config SHA-256: `{report['config_sha256']}`. Raw graph SHA-256: `{raw_hash}`.\n"
        f"- Node CSV SHA-256: `{report['nodes_csv_sha256']}`. Edge CSV SHA-256: `{report['edges_csv_sha256']}`.\n"
        "- Machine-readable files: `data/derived/selected_subnetwork_nodes.csv`, `data/derived/selected_subnetwork_edges.csv`, and `data/derived/selected_subnetwork_report.json`.\n"
    )
    print(json.dumps({"nodes": graph["node_count"], "edges": graph["directed_edge_count"],
                      "synapses": graph["pair_synapses"], "components": components,
                      "document": str(out_doc)}))


if __name__ == "__main__":
    main()
