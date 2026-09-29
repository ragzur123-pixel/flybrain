"""Read the pinned v783 graph as anatomy, with no assumed neural signs or weights."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


NODE_COLUMNS = ("root_id", "role", "side", "status", "annotation_field", "cell_type",
                "hemibrain_type", "position_x", "position_y", "position_z",
                "proofread_member", "snapshot", "annotation_tag")
EDGE_COLUMNS = ("pre_root_id", "post_root_id", "pre_role", "post_role", "pre_side",
                "post_side", "pair_synapses", "neuropil_rows")
OUTPUT_KEYS = (("DNp20", "left"), ("DNp20", "right"),
               ("DNp22", "left"), ("DNp22", "right"))


@dataclass(frozen=True)
class Node:
    root_id: str
    role: str
    side: str


@dataclass(frozen=True)
class Edge:
    pre_index: int
    post_index: int
    pair_synapses: int  # Anatomical count, never a signed model weight.


@dataclass(frozen=True)
class SelectedGraph:
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]
    output_indices: tuple[int, int, int, int]
    nodes_sha256: str
    edges_sha256: str

    @property
    def outputs(self) -> dict[tuple[str, str], int]:
        return dict(zip(OUTPUT_KEYS, self.output_indices))

    def input_indices(self, side: str) -> tuple[int, ...]:
        if side not in {"left", "center", "right"}:
            raise ValueError("Unknown biological side")
        return tuple(i for i, node in enumerate(self.nodes)
                     if node.role == "photoreceptor" and node.side == side)


def _checked_bytes(path: Path, expected: str) -> bytes:
    payload = path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected:
        raise ValueError(f"Selected graph checksum mismatch: {path.name}")
    return payload


def _rows(path: Path, columns: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != columns:
            raise ValueError(f"Selected graph schema mismatch: {path.name}")
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError(f"Malformed selected graph CSV: {path.name}")
    return rows


def load_selected_graph(workspace: Path) -> SelectedGraph:
    """Validate the archived selection and return sparse index-addressed anatomy."""
    root = Path(workspace)
    derived = root / "data/derived"
    report = json.loads((derived / "selected_subnetwork_report.json").read_text(encoding="utf-8"))
    config_path = root / "configs/subnetwork_selection.yaml"
    config = json.loads(_checked_bytes(config_path, report["config_sha256"]))
    node_path = derived / "selected_subnetwork_nodes.csv"
    edge_path = derived / "selected_subnetwork_edges.csv"
    _checked_bytes(node_path, report["nodes_csv_sha256"])
    _checked_bytes(edge_path, report["edges_csv_sha256"])
    node_rows = _rows(node_path, NODE_COLUMNS)
    edge_rows = _rows(edge_path, EDGE_COLUMNS)
    if not node_rows or len(node_rows) != report["node_count"]:
        raise ValueError("Selected graph node count mismatch")
    if len(edge_rows) != report["directed_edge_count"]:
        raise ValueError("Selected graph edge count mismatch")

    nodes = []
    ids: dict[str, int] = {}
    for row in node_rows:
        rid, role, side = row["root_id"], row["role"], row["side"]
        if not rid.isdecimal() or rid in ids or row["status"] != "(blank)" or row["proofread_member"] != "true":
            raise ValueError("Selected graph node provenance or ID invalid")
        if role not in {"photoreceptor", "OCG01", "DNp20", "DNp22"}:
            raise ValueError("Selected graph node role invalid")
        if side not in ({"left", "center", "right"} if role == "photoreceptor" else {"left", "right"}):
            raise ValueError("Selected graph biological side invalid")
        if row["snapshot"] != "FAFB v783" or row["annotation_tag"] != report["annotation_tag"]:
            raise ValueError("Selected graph node snapshot mismatch")
        ids[rid] = len(nodes)
        nodes.append(Node(rid, role, side))
    if Counter(node.role for node in nodes) != {role: count for role, count in report["role_counts"].items() if count}:
        raise ValueError("Selected graph role counts mismatch")

    output_rows = {(node.role, node.side): i for i, node in enumerate(nodes)
                   if node.role in {"DNp20", "DNp22"}}
    if len(output_rows) != 4 or set(output_rows) != set(OUTPUT_KEYS):
        raise ValueError("Selected graph bilateral outputs missing or duplicated")
    if {nodes[i].root_id for i in output_rows.values()} != set(config["output_root_ids"]):
        raise ValueError("Selected graph outputs differ from selection config")

    edges = []
    seen_pairs = set()
    for row in edge_rows:
        pre_id, post_id = row["pre_root_id"], row["post_root_id"]
        if pre_id not in ids or post_id not in ids or (pre_id, post_id) in seen_pairs:
            raise ValueError("Selected graph edge endpoint or duplicate pair invalid")
        seen_pairs.add((pre_id, post_id))
        pre, post = nodes[ids[pre_id]], nodes[ids[post_id]]
        if (row["pre_role"], row["post_role"], row["pre_side"], row["post_side"]) != (
                pre.role, post.role, pre.side, post.side):
            raise ValueError("Selected graph edge metadata mismatch")
        if not ((pre.role == "photoreceptor" and post.role == "OCG01") or
                (pre.role == "OCG01" and post.role in {"DNp20", "DNp22"})):
            raise ValueError("Selected graph edge direction or role path invalid")
        try:
            count = int(row["pair_synapses"])
            neuropil_rows = int(row["neuropil_rows"])
        except ValueError as exc:
            raise ValueError("Selected graph edge count invalid") from exc
        if count < config["min_pair_synapses"] or neuropil_rows < 1:
            raise ValueError("Selected graph edge count below selection rule")
        edges.append(Edge(ids[pre_id], ids[post_id], count))
    if sum(edge.pair_synapses for edge in edges) != report["pair_synapses"]:
        raise ValueError("Selected graph synapse total mismatch")

    parents: dict[int, set[int]] = {i: set() for i in range(len(nodes))}
    for edge in edges:
        parents[edge.post_index].add(edge.pre_index)
    reachable = set(output_rows.values())
    frontier = list(reachable)
    while frontier:
        for parent in parents[frontier.pop()] - reachable:
            reachable.add(parent)
            frontier.append(parent)
    if len(reachable) != len(nodes):
        raise ValueError("Selected graph has nodes without output paths")

    return SelectedGraph(tuple(nodes), tuple(edges),
                         tuple(output_rows[key] for key in OUTPUT_KEYS),
                         report["nodes_csv_sha256"], report["edges_csv_sha256"])
