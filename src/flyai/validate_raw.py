"""Validate the selected v783 raw products without loading the graph into memory."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import psutil
import pyarrow as pa
import pyarrow.ipc as ipc


REQUIRED_COLUMNS = {
    "pre_pt_root_id": pa.int64(),
    "post_pt_root_id": pa.int64(),
    "neuropil": pa.string(),
    "syn_count": pa.int64(),
    **{name: pa.float64() for name in ("gaba_avg", "ach_avg", "glut_avg", "oct_avg", "ser_avg", "da_avg")},
}
PROCESS_LIMITS = ("max_process_memory_bytes", "arrow_batch_rows")
STORAGE_LIMITS = ("max_temporary_bytes",)


class ValidationError(RuntimeError):
    """The input or the validation run failed a declared check."""


def integer_limits(path: Path, section: str, required: tuple[str, ...]) -> dict[str, int]:
    """Read only the plain integer limits from a known resources.yaml section."""
    values: dict[str, int] = {}
    active = False
    for line in path.read_text(encoding="utf-8").splitlines():
        clean = line.split("#", 1)[0].rstrip()
        if not clean:
            continue
        if not line.startswith((" ", "\t")):
            active = clean == f"{section}:"
            continue
        if not active:
            continue
        match = re.fullmatch(r"  ([a-z_]+):\s*(\d+)", clean)
        if not match:
            raise ValidationError(f"Unsupported {section} limit line: {line!r}")
        key, value = match.groups()
        if key in values:
            raise ValidationError(f"Duplicate {section} limit: {key}")
        values[key] = int(value)
    if any(key not in values or values[key] <= 0 for key in required):
        raise ValidationError(f"Missing or nonpositive {section} limit")
    return values


def verify_manifest(workspace: Path, manifest: Path, expected_products: set[str]) -> dict[str, dict[str, str]]:
    """Verify every selected raw file's path, size, SHA-256, and snapshot."""
    raw_dir = (workspace / "data" / "raw").resolve()
    with manifest.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    products: dict[str, dict[str, str]] = {}
    for row in rows:
        name = row["product"]
        path = (workspace / row["path"]).resolve()
        if name in products or path.parent != raw_dir or path.name != name:
            raise ValidationError(f"Duplicate or unsafe manifest product: {name}")
        if row["dataset_id"] != "fafb" or row["snapshot"] != "783":
            raise ValidationError(f"Wrong data lineage for {name}")
        if not path.is_file() or path.stat().st_size != int(row["bytes"]):
            raise ValidationError(f"Missing or wrong-size raw file: {name}")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        if digest.hexdigest() != row["sha256"]:
            raise ValidationError(f"SHA-256 mismatch: {name}")
        products[name] = row
    if set(products) != expected_products:
        raise ValidationError("Manifest product set differs from selected sources")
    return products


def annotation_summary(path: Path, proofread_ids: set[int]) -> dict:
    seen: set[int] = set()
    status: Counter[str] = Counter()
    roles: Counter[tuple[str, str, str]] = Counter()
    rows = missing_id = duplicate_id = absent_from_proofread = 0
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        required = {"root_id", "cell_type", "hemibrain_type", "side", "status"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValidationError("Annotation TSV lacks required columns")
        columns = reader.fieldnames
        for row in reader:
            rows += 1
            if not row["root_id"]:
                missing_id += 1
                continue
            try:
                root_id = int(row["root_id"])
            except ValueError as error:
                raise ValidationError(f"Malformed annotation root ID at row {rows}") from error
            duplicate_id += root_id in seen
            seen.add(root_id)
            absent_from_proofread += root_id not in proofread_ids
            flag = row["status"] or "(blank)"
            status[flag] += 1
            role = None
            if row["cell_type"] == "ocellar retinula cell":
                role = "ocellar_photoreceptor"
            elif row["cell_type"].startswith("OCG01"):
                role = "OCG01"
            elif row["cell_type"] == "DNp22":
                role = "DNp22"
            elif row["hemibrain_type"] in ("DNp20", "DNp28"):
                role = row["hemibrain_type"]
            if role:
                roles[(role, row["side"], flag)] += 1
    return {
        "columns": columns, "rows": rows, "missing_root_ids": missing_id,
        "duplicate_root_ids": duplicate_id, "ids_absent_from_proofread": absent_from_proofread,
        "unique_root_ids": len(seen), "status": dict(status),
        "candidate_roles": [
            {"role": role, "side": side, "status": flag, "count": count}
            for (role, side, flag), count in sorted(roles.items())
        ],
    }


def scan_connections(
    path: Path, proofread_ids: set[int], scratch: Path,
    *, batch_rows: int, max_temp_bytes: int, max_rss_bytes: int,
    min_free_disk_bytes: int, max_batches: int | None = None,
) -> dict:
    """Stream Arrow rows and count exact duplicate (pre, post, neuropil) keys on disk."""
    if scratch.exists():
        raise ValidationError(f"Scratch database already exists: {scratch}")
    if shutil.disk_usage(scratch.parent).free < min_free_disk_bytes + max_temp_bytes:
        raise ValidationError("Insufficient free disk for scratch cap and free-disk floor")
    process = psutil.Process()
    peak_rss = process.memory_info().rss
    started = time.monotonic()
    conn = sqlite3.connect(scratch)
    try:
        conn.execute("PRAGMA journal_mode=OFF")
        conn.execute("PRAGMA synchronous=OFF")
        conn.execute("PRAGMA temp_store=FILE")
        conn.execute("PRAGMA cache_size=-65536")
        conn.execute(
            "CREATE TABLE edge_keys (pre INTEGER, post INTEGER, neuropil TEXT, "
            "PRIMARY KEY (pre, post, neuropil)) WITHOUT ROWID"
        )
        with pa.memory_map(str(path), "r") as source:
            reader = ipc.open_file(source)
            schema = reader.schema
            for name, expected_type in REQUIRED_COLUMNS.items():
                if name not in schema.names or schema.field(name).type != expected_type:
                    raise ValidationError(f"Missing or wrong-type connection column: {name}")
            summary = {
                "schema": [{"name": field.name, "type": str(field.type)} for field in schema],
                "record_batches": reader.num_record_batches,
                "batches_scanned": 0, "complete": max_batches is None,
                "rows": 0, "nulls": {name: 0 for name in schema.names},
                "self_loops": 0, "nonpositive_syn_count": 0,
                "pre_ids_absent_from_proofread": 0, "post_ids_absent_from_proofread": 0,
                "duplicate_pair_neuropil_rows": 0,
                "syn_count_min": None, "syn_count_max": None, "syn_count_total": 0,
            }
            limit = reader.num_record_batches if max_batches is None else min(max_batches, reader.num_record_batches)
            for batch_index in range(limit):
                batch = reader.get_batch(batch_index)
                summary["batches_scanned"] += 1
                for start in range(0, batch.num_rows, batch_rows):
                    chunk = batch.slice(start, batch_rows)
                    count = chunk.num_rows
                    for name in schema.names:
                        summary["nulls"][name] += chunk.column(name).null_count
                    for name in ("pre_pt_root_id", "post_pt_root_id", "neuropil", "syn_count"):
                        if chunk.column(name).null_count:
                            raise ValidationError(f"Null required field {name} in batch {batch_index}")
                    pre = chunk.column("pre_pt_root_id").to_numpy()
                    post = chunk.column("post_pt_root_id").to_numpy()
                    weights = chunk.column("syn_count").to_numpy()
                    neuropils = chunk.column("neuropil").to_pylist()
                    summary["rows"] += count
                    summary["self_loops"] += int(np.count_nonzero(pre == post))
                    summary["nonpositive_syn_count"] += int(np.count_nonzero(weights <= 0))
                    summary["pre_ids_absent_from_proofread"] += sum(int(value) not in proofread_ids for value in pre)
                    summary["post_ids_absent_from_proofread"] += sum(int(value) not in proofread_ids for value in post)
                    summary["syn_count_total"] += int(weights.sum())
                    low, high = int(weights.min()), int(weights.max())
                    summary["syn_count_min"] = low if summary["syn_count_min"] is None else min(low, summary["syn_count_min"])
                    summary["syn_count_max"] = high if summary["syn_count_max"] is None else max(high, summary["syn_count_max"])
                    before = conn.total_changes
                    conn.executemany(
                        "INSERT OR IGNORE INTO edge_keys (pre, post, neuropil) VALUES (?, ?, ?)",
                        ((int(a), int(b), c) for a, b, c in zip(pre, post, neuropils)),
                    )
                    summary["duplicate_pair_neuropil_rows"] += count - (conn.total_changes - before)
                    peak_rss = max(peak_rss, process.memory_info().rss)
                    if peak_rss > max_rss_bytes:
                        raise ValidationError("Process RSS exceeded configured memory cap")
                    if scratch.stat().st_size > max_temp_bytes:
                        raise ValidationError("Scratch database exceeded configured temporary-space cap")
                    if shutil.disk_usage(scratch.parent).free < min_free_disk_bytes:
                        raise ValidationError("Free disk fell below configured floor")
                conn.commit()
        summary["scratch_peak_bytes"] = scratch.stat().st_size
        summary["peak_rss_bytes"] = peak_rss
        summary["elapsed_seconds"] = round(time.monotonic() - started, 2)
        return summary
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--max-batches", type=int, help="Exploratory bounded run; omit for full validation")
    args = parser.parse_args(argv)
    workspace = args.workspace.resolve()
    scratch = workspace / "data" / "derived" / "validation_keys.sqlite"
    report_path = workspace / "data" / "derived" / "full_validation.json"
    try:
        if args.max_batches is not None and args.max_batches <= 0:
            raise ValidationError("max-batches must be positive")
        config = workspace / "configs" / "resources.yaml"
        processing = integer_limits(config, "processing", PROCESS_LIMITS)
        storage = integer_limits(config, "storage", STORAGE_LIMITS)
        download = integer_limits(config, "download", ("min_free_disk_bytes_after",))
        sources = json.loads((workspace / "configs" / "data_sources.json").read_text(encoding="utf-8"))
        expected = {item["product"] for item in sources["products"]}
        manifest = verify_manifest(workspace, workspace / "data" / "raw" / "manifest.csv", expected)
        roots = np.load(workspace / "data" / "raw" / "proofread_root_ids_783.npy", mmap_mode="r")
        if roots.dtype != np.uint64 or roots.ndim != 1:
            raise ValidationError("Wrong proofread-ID array dtype or shape")
        root_set = set(map(int, roots))
        if len(root_set) != len(roots):
            raise ValidationError("Duplicate proofread root IDs")
        annotations = annotation_summary(
            workspace / "data" / "raw" / "Supplemental_file1_neuron_annotations_v2.1.0.tsv", root_set
        )
        if annotations["missing_root_ids"] or annotations["duplicate_root_ids"] or annotations["ids_absent_from_proofread"]:
            raise ValidationError("Annotation ID integrity failed")
        scratch.parent.mkdir(parents=True, exist_ok=True)
        connections = scan_connections(
            workspace / "data" / "raw" / "proofread_connections_783.feather", root_set, scratch,
            batch_rows=processing["arrow_batch_rows"],
            max_temp_bytes=storage["max_temporary_bytes"],
            max_rss_bytes=processing["max_process_memory_bytes"],
            min_free_disk_bytes=download["min_free_disk_bytes_after"],
            max_batches=args.max_batches,
        )
        report = {
            "dataset_id": "fafb", "snapshot": "783",
            "manifest_sha256": {name: row["sha256"] for name, row in manifest.items()},
            "proofread_root_ids": {"count": len(roots), "dtype": str(roots.dtype)},
            "annotations": annotations, "connections": connections,
        }
        temporary_report = report_path.with_suffix(".json.tmp")
        temporary_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        temporary_report.replace(report_path)
        scratch.unlink()
        print(json.dumps({
            "report": str(report_path), "complete": connections["complete"],
            "rows": connections["rows"], "duplicates": connections["duplicate_pair_neuropil_rows"],
            "peak_rss_bytes": connections["peak_rss_bytes"], "elapsed_seconds": connections["elapsed_seconds"],
        }, sort_keys=True))
        return 0
    except (ValidationError, OSError, ValueError, KeyError, sqlite3.Error) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
