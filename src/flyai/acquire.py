"""Bounded, checksum-verified acquisition of the selected public raw products.

This module only downloads immutable inputs. It does not parse or interpret them.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


MANIFEST_FIELDS = (
    "dataset_id", "snapshot", "product", "source_url", "downloaded_at_utc",
    "path", "bytes", "sha256", "license", "citation",
)
LIMIT_KEYS = (
    "max_file_bytes", "max_total_bytes", "min_free_disk_bytes_after",
    "timeout_seconds", "stream_chunk_bytes",
)


class AcquisitionError(RuntimeError):
    """A file failed a resource, provenance, or integrity check."""


def load_download_limits(path: Path) -> dict[str, int]:
    """Read the simple integer download section of resources.yaml, rejecting ambiguity."""
    values: dict[str, int] = {}
    in_download = False
    for line in path.read_text(encoding="utf-8").splitlines():
        clean = line.split("#", 1)[0].rstrip()
        if not clean:
            continue
        if not line.startswith((" ", "\t")):
            in_download = clean == "download:"
            continue
        if not in_download:
            continue
        match = re.fullmatch(r"  ([a-z_]+):\s*(\d+)", clean)
        if not match:
            raise AcquisitionError(f"Unsupported download limit line: {line!r}")
        key, value = match.groups()
        if key not in LIMIT_KEYS or key in values:
            raise AcquisitionError(f"Unknown or duplicate download limit: {key}")
        values[key] = int(value)
    if set(values) != set(LIMIT_KEYS) or any(value <= 0 for value in values.values()):
        raise AcquisitionError("Missing or nonpositive download limits")
    return values


def git_blob_hash(path: Path, size: int, chunk_bytes: int) -> str:
    digest = hashlib.sha1()
    digest.update(f"blob {size}\0".encode("ascii"))
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_has_product(manifest: Path, product: str) -> bool:
    if not manifest.exists():
        return False
    with manifest.open("r", encoding="utf-8", newline="") as stream:
        return any(row.get("product") == product for row in csv.DictReader(stream))


def download_product(
    workspace: Path, product: dict, limits: dict[str, int],
    dataset_id: str, snapshot: str,
) -> dict[str, str]:
    """Download one product to .part, verify it, then publish path and manifest."""
    workspace = workspace.resolve()
    raw_dir = (workspace / "data" / "raw").resolve()
    raw_dir.mkdir(parents=True, exist_ok=True)
    relative_path = Path(product["path"])
    target = (workspace / relative_path).resolve()
    if target.parent != raw_dir or target.name != product["product"]:
        raise AcquisitionError("Product path must be a direct data/raw child named as product")
    part = target.with_name(target.name + ".part")
    manifest = raw_dir / "manifest.csv"
    if target.exists() or part.exists() or _manifest_has_product(manifest, product["product"]):
        raise AcquisitionError(f"Product or partial file already exists: {target.name}")

    expected = int(product["expected_bytes"])
    if expected <= 0 or expected > limits["max_file_bytes"]:
        raise AcquisitionError("Published size exceeds the per-file cap")
    free_before = shutil.disk_usage(raw_dir).free
    if free_before - expected < limits["min_free_disk_bytes_after"]:
        raise AcquisitionError("Insufficient free disk for expected product and floor")

    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    total = 0
    request = urllib.request.Request(product["source_url"], headers={"User-Agent": "FlyAI-research-acquisition/1"})
    try:
        with urllib.request.urlopen(request, timeout=limits["timeout_seconds"]) as response, part.open("xb") as output:
            while chunk := response.read(limits["stream_chunk_bytes"]):
                total += len(chunk)
                if total > expected or total > limits["max_file_bytes"]:
                    raise AcquisitionError("Download exceeded expected size or per-file cap")
                output.write(chunk)
                md5.update(chunk)
                sha256.update(chunk)
                if shutil.disk_usage(raw_dir).free < limits["min_free_disk_bytes_after"]:
                    raise AcquisitionError("Free disk fell below the configured floor")
            output.flush()
            os.fsync(output.fileno())
        if total != expected:
            raise AcquisitionError(f"Size mismatch: expected {expected}, received {total}")
        checksum_type = product["checksum_type"]
        if checksum_type == "md5":
            actual = md5.hexdigest()
        elif checksum_type == "git_blob_sha1":
            actual = git_blob_hash(part, total, limits["stream_chunk_bytes"])
        else:
            raise AcquisitionError(f"Unsupported checksum type: {checksum_type}")
        if actual.lower() != product["checksum"].lower():
            raise AcquisitionError(f"Checksum mismatch for {product['product']}")
        # Keep the raw file and its manifest in one directory; never overwrite.
        part.rename(target)
        row = {
            "dataset_id": dataset_id,
            "snapshot": snapshot,
            "product": product["product"],
            "source_url": product["source_url"],
            "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
            "path": relative_path.as_posix(),
            "bytes": str(total),
            "sha256": sha256.hexdigest(),
            "license": product["license"],
            "citation": product["citation"],
        }
        with manifest.open("a", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS)
            if manifest.stat().st_size == 0:
                writer.writeheader()
            writer.writerow(row)
        return row
    except Exception:
        # Keep a failed .part file as evidence; it cannot be parsed as a raw product.
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--product", required=True, help="Exact product name from configs/data_sources.json")
    args = parser.parse_args(argv)
    workspace = args.workspace.resolve()
    try:
        limits = load_download_limits(workspace / "configs" / "resources.yaml")
        sources = json.loads((workspace / "configs" / "data_sources.json").read_text(encoding="utf-8"))
        products = sources["products"]
        if sum(int(item["expected_bytes"]) for item in products) > limits["max_total_bytes"]:
            raise AcquisitionError("Selected product set exceeds total-download cap")
        matches = [item for item in products if item["product"] == args.product]
        if len(matches) != 1:
            raise AcquisitionError("Product must match exactly one configured source")
        if sources["dataset_id"] != "fafb" or str(sources["snapshot"]) != "783":
            raise AcquisitionError("Configured data lineage differs from selected FAFB v783")
        row = download_product(workspace, matches[0], limits, sources["dataset_id"], str(sources["snapshot"]))
        print(json.dumps({key: row[key] for key in ("product", "bytes", "sha256", "path")}, sort_keys=True))
        return 0
    except (AcquisitionError, OSError, ValueError, KeyError) as error:
        print(f"acquisition failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
