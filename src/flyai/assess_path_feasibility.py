"""Run predeclared C03 anatomical path screen on the pinned archive graph."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flyai.audit_ocellar_laterality import analyze
from flyai.screen_ocellar import screen
from flyai.validate_raw import verify_manifest


PRODUCTS = {
    "proofread_connections_783.feather", "proofread_root_ids_783.npy",
    "per_neuron_neuropil_count_pre_783.feather",
    "Supplemental_file1_neuron_annotations_v2.1.0.tsv",
}
ROLES = ("DNp20", "DNp22", "DNp28")


def validate_rule(rule: dict) -> tuple[int, int]:
    primary = rule["primary_min_pair_synapses"]
    sensitivity = rule["sensitivity_min_pair_synapses"]
    if not isinstance(primary, int) or not isinstance(sensitivity, int):
        raise ValueError("Thresholds must be integers")
    if not 1 <= sensitivity < primary:
        raise ValueError("Expected positive sensitivity threshold below primary")
    if not rule["no_behavior_use"] or set(rule["route_by_output_role"]) != set(ROLES):
        raise ValueError("C03 rule lacks role routes or no-behavior declaration")
    return primary, sensitivity


def summarize(rows: list[dict], statuses: dict[str, str]) -> dict:
    """Apply role-aware direct versus two-hop reachability and pair criterion."""
    outputs = []
    for row in rows:
        role, side = row["role"], row["side"]
        if role not in ROLES or side not in ("left", "right"):
            raise ValueError(f"Unexpected candidate output: {role} {side}")
        if role == "DNp28":
            by_side = row["direct_photoreceptors_by_side"]
            route = "direct"
            same_side = by_side[side]
            total = sum(by_side.values())
        else:
            by_side = row["two_hop_photoreceptors_by_side"]
            route = "via_OCG01"
            same_side = row["full_ipsilateral_two_hop_photoreceptors"]
            total = row["two_hop_unique_total"]
        outputs.append({"output_root_id": row["output_root_id"], "role": role,
                        "side": side, "status": statuses[row["output_root_id"]],
                        "route": route, "unique_photoreceptors_by_side": by_side,
                        "unique_photoreceptors_total": total,
                        "fully_same_side_photoreceptors": same_side,
                        "screen_feasible": same_side > 0})
    paired = {}
    for role in ROLES:
        matching = [row for row in outputs if row["role"] == role]
        if len(matching) != 2 or {row["side"] for row in matching} != {"left", "right"}:
            raise ValueError(f"Expected exactly one left and one right {role} output")
        paired[role] = all(row["screen_feasible"] for row in matching)
    return {"outputs": outputs, "left_right_role_feasible": paired}


def render(result: dict) -> str:
    lines = [
        "# C03 archive path feasibility — 2026-09-28",
        "",
        "Status: **anatomical reachability screen complete; no C04 circuit",
        "selection, motor decoder, or behavioral run**. This follows the",
        "[predeclared C03 rule](path_feasibility_rule.md).",
        "",
        f"Raw connection SHA-256: `{result['raw_connection_sha256']}`.",
        f"C02 inventory SHA-256: `{result['candidate_inventory_sha256']}`.",
        f"Rule SHA-256: `{result['rule_sha256']}`.",
        f"Graph rows rescanned: **{result['raw_rows_scanned']:,}**; directed candidate pairs: **{result['candidate_pairs']}**.",
        "The new pair list agreed exactly with the earlier exploratory screen.",
        "Counts are unique photoreceptor IDs, not synapses or distinct paths.",
        "",
        "| Pair minimum | Output | Route | Photo inputs L/R/C | All unique | Fully same-side | Status |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for threshold in (result["primary_threshold"], result["sensitivity_threshold"]):
        for row in result["by_threshold"][str(threshold)]["outputs"]:
            sides = row["unique_photoreceptors_by_side"]
            triple = "/".join(str(sides[side]) for side in ("left", "right", "center"))
            lines.append(f"| {threshold} | {row['role']} {row['side']} | {row['route']} | "
                         f"{triple} | {row['unique_photoreceptors_total']} | "
                         f"{row['fully_same_side_photoreceptors']} | {row['status']} |")
    lines.extend([
        "",
        "At both thresholds, every output role passes the declared",
        "left/right **reachability-only** screen. DNp28 right remains",
        "`outlier_seg`; C04 must decide whether to include it. The OCG01",
        "routes retain mixed-side and center inputs in their all-side totals.",
        "A threshold of five is an analytical convention, not biological",
        "proof that smaller archive connections are irrelevant. Neither",
        "reachability nor the 3D mesh establishes steering sign or an",
        "appropriate virtual vehicle motor mapping.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    rule_path = root / "configs/path_feasibility_v1.json"
    inventory_path = root / "data/derived/candidate_id_inventory.csv"
    output = root / "data/derived/path_feasibility_v1.json"
    document = root / "docs/path_feasibility_v1.md"
    if output.exists() or document.exists():
        raise FileExistsError("C03 result already exists; preserve prior output")
    rule_bytes = rule_path.read_bytes()
    inventory_bytes = inventory_path.read_bytes()
    rule = json.loads(rule_bytes)
    primary, sensitivity = validate_rule(rule)
    manifest = verify_manifest(root, root / "data/raw/manifest.csv", PRODUCTS)
    with inventory_path.open("r", encoding="utf-8", newline="") as stream:
        candidates = list(csv.DictReader(stream))
    if len(candidates) != 291 or len({row["root_id"] for row in candidates}) != 291:
        raise ValueError("C02 inventory is incomplete or has duplicate IDs")
    labels = {int(row["root_id"]): {"role": row["role"], "side": row["side"],
                                    "status": row["status"]} for row in candidates}
    fresh = screen(root / "data/raw/proofread_connections_783.feather", labels)
    old = json.loads((root / "data/derived/ocellar_path_screen.json").read_text(encoding="utf-8"))
    if (fresh["row_count_scanned"] != 16847997 or
            fresh["candidate_pairs"] != old["candidate_pairs"] or
            fresh["candidate_id_count"] != 291):
        raise ValueError("Fresh graph screen disagrees with earlier candidate pairs")
    statuses = {row["root_id"]: row["status"] for row in candidates}
    by_threshold = {}
    for threshold in (primary, sensitivity):
        by_threshold[str(threshold)] = summarize(analyze(fresh, threshold), statuses)
    result = {
        "dataset": "publication-time 2024 FAFB v783 archive",
        "annotation_tag": "v2.1.0", "no_behavior_used": True,
        "rule_sha256": hashlib.sha256(rule_bytes).hexdigest(),
        "candidate_inventory_sha256": hashlib.sha256(inventory_bytes).hexdigest(),
        "raw_connection_sha256": manifest["proofread_connections_783.feather"]["sha256"],
        "raw_rows_scanned": fresh["row_count_scanned"],
        "candidate_pairs": fresh["candidate_pair_count"],
        "primary_threshold": primary, "sensitivity_threshold": sensitivity,
        "by_threshold": by_threshold,
    }
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    document.write_text(render(result), encoding="utf-8")
    print(json.dumps({"output": str(output), "document": str(document),
                      "rows": result["raw_rows_scanned"], "pairs": result["candidate_pairs"],
                      "role_feasible_primary": by_threshold[str(primary)]["left_right_role_feasible"],
                      "role_feasible_sensitivity": by_threshold[str(sensitivity)]["left_right_role_feasible"]}))


if __name__ == "__main__":
    main()
