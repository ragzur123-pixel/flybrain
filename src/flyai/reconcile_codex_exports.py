"""Compare pinned v783 archive pairs with explicit Codex CSV exports."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse


EXPECTED_COLUMNS = ["From", "To", "Neuropil", "Synapses", "Neuro Transmitter"]


def verify_export(workspace: Path, item: dict) -> list[dict]:
    post = item["post_root_id"]
    export_dir = (workspace / "data/derived/codex_portal_2026-09-26").resolve()
    path = (workspace / item["path"]).resolve()
    if path.parent != export_dir or path.name != f"{post}.csv":
        raise ValueError(f"Unexpected Codex export path for {post}")
    url = urlparse(item["source_url"])
    query = parse_qs(url.query)
    if (url.scheme, url.netloc, url.path) != ("https", "codex.flywire.ai", "/app/connectivity"):
        raise ValueError(f"Unexpected Codex source URL for {post}")
    for key, value in {"data_version": "783", "dataset": "fafb", "download": "csv",
                       "cell_names_or_ids": f"root_id == {post}"}.items():
        if query.get(key) != [value]:
            raise ValueError(f"Wrong Codex {key} for {post}")
    content = path.read_bytes()
    if len(content) != int(item["bytes"]) or hashlib.sha256(content).hexdigest() != item["sha256"]:
        raise ValueError(f"Codex export hash or size changed for {post}")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError(f"Unexpected Codex CSV columns for {post}")
        rows = list(reader)
    if any(post not in (row["From"], row["To"]) for row in rows):
        raise ValueError(f"Codex export includes an off-target row for {post}")
    return rows


def reconcile(audit: dict, manifest: list[dict], workspace: Path) -> dict:
    if audit["portal_verified"]:
        raise ValueError("Expected a pending local audit")
    by_post = {item["post_root_id"]: item for item in manifest}
    if len(by_post) != len(manifest) or set(by_post) != {x["post_root_id"] for x in audit["checks"]}:
        raise ValueError("Codex export set differs from planned postsynaptic cells")
    export_rows = {post: verify_export(workspace, item) for post, item in by_post.items()}
    results = []
    for index, pair in enumerate(audit["checks"], 1):
        pre, post = pair["pre_root_id"], pair["post_root_id"]
        rows = export_rows[post]
        forward = sorted(({"neuropil": row["Neuropil"], "syn_count": int(row["Synapses"]),
                           "nt_prediction": row["Neuro Transmitter"]}
                          for row in rows if (row["From"], row["To"]) == (pre, post)),
                         key=lambda row: row["neuropil"])
        reverse = sorted(({"neuropil": row["Neuropil"], "syn_count": int(row["Synapses"])}
                          for row in rows if (row["From"], row["To"]) == (post, pre)),
                         key=lambda row: row["neuropil"])
        portal_total = sum(row["syn_count"] for row in forward)
        archive_regions = {row["neuropil"]: row["syn_count"] for row in pair["forward_rows"]}
        portal_regions = {row["neuropil"]: row["syn_count"] for row in forward}
        status = "matched" if archive_regions == portal_regions else "discrepancy"
        results.append({
            "number": index, "pre_root_id": pre, "post_root_id": post,
            "pre_role": pair["pre_role"], "post_role": pair["post_role"],
            "pre_side": pair["pre_side"], "post_side": pair["post_side"],
            "archive_synapses": pair["forward_synapses"], "codex_synapses": portal_total,
            "delta": portal_total - pair["forward_synapses"],
            "archive_rows": pair["forward_rows"], "codex_rows": forward,
            "archive_reverse_synapses": pair["reverse_synapses"],
            "codex_reverse_synapses": sum(row["syn_count"] for row in reverse),
            "codex_reverse_rows": reverse, "status": status,
            "codex_url": by_post[post]["source_url"],
            "codex_export_sha256": by_post[post]["sha256"],
        })
    return {"dataset": "FAFB v783", "comparison": "publication-time archive vs current Codex export",
            "archive_sha256": audit["raw_sha256"], "codex_exports": len(manifest),
            "pairs": results, "matched": sum(x["status"] == "matched" for x in results),
            "discrepant": sum(x["status"] == "discrepancy" for x in results)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    audit = json.loads((root / "data/derived/manual_pair_raw_audit.json").read_text(encoding="utf-8"))
    with (root / "data/derived/codex_portal_2026-09-26/manifest.csv").open(
            "r", encoding="utf-8", newline="") as stream:
        manifest = list(csv.DictReader(stream))
    result = reconcile(audit, manifest, root)
    output = root / "data/derived/codex_reconciliation.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "matched": result["matched"],
                      "discrepant": result["discrepant"]}))


if __name__ == "__main__":
    main()
