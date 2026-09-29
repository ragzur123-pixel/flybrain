"""Compare C04 anatomical option footprints without selecting a controller."""

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

from flyai.validate_raw import verify_manifest


OPTIONS = {
    "ocg_family": ("DNp20", "DNp22"),
    "dnp20_pair": ("DNp20",),
    "dnp22_pair": ("DNp22",),
    "dnp28_direct": ("DNp28",),
}
PRODUCTS = {
    "proofread_connections_783.feather", "proofread_root_ids_783.npy",
    "per_neuron_neuropil_count_pre_783.feather",
    "Supplemental_file1_neuron_annotations_v2.1.0.tsv",
}


def option_footprint(pairs: list[dict], inventory: dict[str, dict],
                     roles: tuple[str, ...], threshold: int,
                     strict_same_side: bool, include_graph: bool = False) -> dict:
    """Keep directed edges on complete role-correct paths at one threshold."""
    if threshold < 1:
        raise ValueError("Threshold must be positive")
    outputs = {rid for rid, row in inventory.items() if row["role"] in roles}
    expected = 2 * len(roles)
    if len(outputs) != expected:
        raise ValueError("Expected one left and one right output per role")
    eligible = {}
    for edge in pairs:
        key = (edge["pre_root_id"], edge["post_root_id"])
        if key in eligible:
            raise ValueError(f"Duplicate ordered pair: {key}")
        if edge["pair_synapses"] >= threshold:
            eligible[key] = edge
    photos_to_ocg = defaultdict(list)
    ocg_to_outputs = defaultdict(list)
    direct = defaultdict(list)
    for edge in eligible.values():
        pre, post = edge["pre_root_id"], edge["post_root_id"]
        if pre not in inventory or post not in inventory:
            raise ValueError("Pair has an ID absent from the C02 inventory")
        pre_role, post_role = inventory[pre]["role"], inventory[post]["role"]
        if edge["pre_role"] != pre_role or edge["post_role"] != post_role:
            raise ValueError("Pair role disagrees with the C02 inventory")
        if (edge["pre_side"] != inventory[pre]["side"] or
                edge["post_side"] != inventory[post]["side"]):
            raise ValueError("Pair side disagrees with the C02 inventory")
        if pre_role == "photoreceptor" and post_role == "OCG01":
            photos_to_ocg[post].append(edge)
        elif pre_role == "OCG01" and post in outputs and post_role != "DNp28":
            ocg_to_outputs[post].append(edge)
        elif pre_role == "photoreceptor" and post in outputs and post_role == "DNp28":
            direct[post].append(edge)
    included = {}
    per_output = []
    for output in sorted(outputs):
        output_row = inventory[output]
        seen_photos = set()
        same_side_photos = set()
        paths = 0
        if output_row["role"] == "DNp28":
            for edge in direct[output]:
                photo = edge["pre_root_id"]
                same = inventory[photo]["side"] == output_row["side"]
                if strict_same_side and not same:
                    continue
                included[(photo, output)] = edge
                seen_photos.add(photo)
                if same:
                    same_side_photos.add(photo)
                paths += 1
        else:
            for downstream in ocg_to_outputs[output]:
                ocg = downstream["pre_root_id"]
                for upstream in photos_to_ocg[ocg]:
                    photo = upstream["pre_root_id"]
                    same = (inventory[photo]["side"] == inventory[ocg]["side"] ==
                            output_row["side"])
                    if strict_same_side and not same:
                        continue
                    included[(photo, ocg)] = upstream
                    included[(ocg, output)] = downstream
                    seen_photos.add(photo)
                    if same:
                        same_side_photos.add(photo)
                    paths += 1
        per_output.append({
            "root_id": output, "role": output_row["role"],
            "side": output_row["side"], "status": output_row["status"],
            "unique_photoreceptors": len(seen_photos),
            "fully_same_side_photoreceptors": len(same_side_photos),
            "distinct_ordered_role_paths": paths,
        })
    used = set(outputs)
    for pre, post in included:
        used.add(pre)
        used.add(post)
    by_role = {role: sum(inventory[rid]["role"] == role for rid in used)
               for role in ("photoreceptor", "OCG01", "DNp20", "DNp22", "DNp28")}
    result = {
        "node_count": len(used), "directed_edge_count": len(included),
        "pair_synapses": sum(edge["pair_synapses"] for edge in included.values()),
        "roles": by_role, "outputs": per_output,
        "all_outputs_reachable": all(row["unique_photoreceptors"] > 0 for row in per_output),
    }
    if include_graph:
        result["node_ids"] = sorted(used, key=int)
        result["edges"] = [included[key] for key in sorted(included, key=lambda key: (int(key[0]), int(key[1])))]
    return result


def render(report: dict) -> str:
    lines = [
        "# C04 candidate option footprint — 2026-09-28", "",
        "**Anatomical comparison only.** This report does not select a circuit,",
        "cap, input encoder, output decoder, or motor sign. It filters the",
        "C03-verified candidate ordered-pair list; it does not rescan the raw",
        "graph independently. Each edge meets the stated pair-summed minimum,",
        "and every retained edge lies on at least one complete role-correct",
        "input-to-output path. `strict_same_side` is a hypothetical reduction",
        "that drops other-side and center paths, not a claim about physiology.", "",
        f"Raw graph SHA-256: `{report['raw_connection_sha256']}`.",
        f"Saved candidate-pair screen SHA-256: `{report['pair_screen_sha256']}`.",
        f"C02 inventory SHA-256: `{report['inventory_sha256']}`.", "",
        "| Pair minimum | Option | Side policy | Nodes | Directed edges | Pair-summed synapses | Photo / OCG / outputs | Every output reachable |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for threshold in (report["primary_threshold"], report["sensitivity_threshold"]):
        for name in OPTIONS:
            for policy in ("all_sides", "strict_same_side"):
                row = report["options"][str(threshold)][name][policy]
                role_counts = row["roles"]
                outputs = sum(role_counts[r] for r in ("DNp20", "DNp22", "DNp28"))
                lines.append(
                    f"| {threshold} | {name} | {policy} | {row['node_count']} | "
                    f"{row['directed_edge_count']} | {row['pair_synapses']} | "
                    f"{role_counts['photoreceptor']} / {role_counts['OCG01']} / {outputs} | "
                    f"{'yes' if row['all_outputs_reachable'] else 'no'} |"
                )
    lines += [
        "", "These counts describe the induced role-path graph, not the full",
        "connectome or a final reduced network. Pair-summed synapses count",
        "each retained directed edge once, even if it serves multiple paths.",
        "A strict same-side graph may discard real cross-side/center anatomy.",
        "Right DNp28 retains its `outlier_seg` annotation in the machine-readable",
        "output. Blank status on other candidates is not quality assurance.",
        "No option is ranked by simulated performance or chosen here.", "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    output = root / "data/derived/c04_option_footprints.json"
    document = root / "docs/c04_option_footprints.md"
    if output.exists() or document.exists():
        raise FileExistsError("C04 footprint output already exists; preserve it")
    c03 = json.loads((root / "data/derived/path_feasibility_v1.json").read_text(encoding="utf-8"))
    screen_bytes = (root / "data/derived/ocellar_path_screen.json").read_bytes()
    screen = json.loads(screen_bytes)
    inventory_bytes = (root / "data/derived/candidate_id_inventory.csv").read_bytes()
    with (root / "data/derived/candidate_id_inventory.csv").open(encoding="utf-8", newline="") as stream:
        inventory = {row["root_id"]: row for row in csv.DictReader(stream)}
    if len(inventory) != 291 or screen["candidate_pair_count"] != c03["candidate_pairs"]:
        raise ValueError("C02/C03 candidate packet count mismatch")
    if hashlib.sha256(inventory_bytes).hexdigest() != c03["candidate_inventory_sha256"]:
        raise ValueError("C02 inventory hash disagrees with C03")
    manifest = verify_manifest(root, root / "data/raw/manifest.csv", PRODUCTS)
    raw_hash = manifest["proofread_connections_783.feather"]["sha256"]
    if raw_hash != c03["raw_connection_sha256"]:
        raise ValueError("Raw graph hash disagrees with C03")
    options = {}
    for threshold in (c03["primary_threshold"], c03["sensitivity_threshold"]):
        options[str(threshold)] = {
            name: {
                "all_sides": option_footprint(screen["candidate_pairs"], inventory, roles,
                                               threshold, False),
                "strict_same_side": option_footprint(screen["candidate_pairs"], inventory,
                                                     roles, threshold, True),
            }
            for name, roles in OPTIONS.items()
        }
        expected = {(row["role"], row["side"]): row
                    for row in c03["by_threshold"][str(threshold)]["outputs"]}
        for option in options[str(threshold)].values():
            for row in option["all_sides"]["outputs"]:
                reference = expected[(row["role"], row["side"])]
                if (row["unique_photoreceptors"] != reference["unique_photoreceptors_total"]
                        or row["fully_same_side_photoreceptors"] !=
                        reference["fully_same_side_photoreceptors"]):
                    raise ValueError("C04 all-side path counts disagree with C03")
            for row in option["strict_same_side"]["outputs"]:
                if row["unique_photoreceptors"] != expected[(row["role"], row["side"])][
                        "fully_same_side_photoreceptors"]:
                    raise ValueError("C04 strict-side path counts disagree with C03")
    report = {
        "status": "C04 anatomy-only comparison; no selection",
        "raw_connection_sha256": raw_hash,
        "pair_screen_sha256": hashlib.sha256(screen_bytes).hexdigest(),
        "inventory_sha256": hashlib.sha256(inventory_bytes).hexdigest(),
        "primary_threshold": c03["primary_threshold"],
        "sensitivity_threshold": c03["sensitivity_threshold"],
        "options": options,
    }
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    document.write_text(render(report), encoding="utf-8")
    print(json.dumps({"output": str(output), "document": str(document),
                      "primary": options[str(c03["primary_threshold"])]}))


if __name__ == "__main__":
    main()
