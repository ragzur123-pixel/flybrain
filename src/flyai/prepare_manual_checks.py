"""Prepare ten deterministic v783 candidate-pair lookups for manual Codex review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


STRATA = (
    ("photoreceptor", "OCG01", "left", "left", 1),
    ("photoreceptor", "OCG01", "right", "right", 1),
    ("photoreceptor", "OCG01", "center", "left", 1),
    ("photoreceptor", "OCG01", "center", "right", 1),
    ("photoreceptor", "DNp28", "left", "left", 1),
    ("photoreceptor", "DNp28", "right", "right", 1),
    ("OCG01", "DNp20", "left", "left", 1),
    ("OCG01", "DNp20", "right", "right", 1),
    ("OCG01", "DNp22", "left", "left", 1),
    ("OCG01", "DNp22", "right", "right", 1),
)


def select_checks(pairs: list[dict]) -> list[dict]:
    """Take the strongest visible pairs per stratum, diversifying source IDs."""
    selected: list[dict] = []
    for pre_role, post_role, pre_side, post_side, needed in STRATA:
        eligible = sorted(
            (
                pair for pair in pairs
                if pair["pre_role"] == pre_role
                and pair["post_role"] == post_role
                and pair["pre_side"] == pre_side
                and pair["post_side"] == post_side
                and pair["pair_synapses"] >= 5
            ),
            key=lambda pair: (-pair["pair_synapses"], pair["pre_root_id"], pair["post_root_id"]),
        )
        used_pre: set[str] = set()
        chosen: list[dict] = []
        for pair in eligible:
            if pair["pre_root_id"] in used_pre:
                continue
            chosen.append(pair)
            used_pre.add(pair["pre_root_id"])
            if len(chosen) == needed:
                break
        if len(chosen) != needed:
            raise ValueError(f"Insufficient eligible pairs for {pre_role}/{post_role} {pre_side}/{post_side}")
        selected.extend(chosen)
    return selected


def worksheet(checks: list[dict], screen_path: str) -> str:
    lines = [
        "# P1 manual FlyWire/Codex connection checks",
        "",
        "Status: **pending independent Codex review**. These ten ordered pairs were selected",
        "deterministically from the full v783 local path screen. The values below are local",
        "pair-summed synapse counts across neuropil rows, not portal observations.",
        "",
        f"Source: `{screen_path}`; selector: `src/flyai/prepare_manual_checks.py`.",
        "Use FAFB v783 in Codex. For each pair, inspect the presynaptic cell's outputs",
        "or the postsynaptic cell's inputs. Record the displayed direction, count, page",
        "or screenshot reference, and any difference in the blank review columns. Codex",
        "may apply its display threshold or an aggregation rule different from this file.",
        "Do not mark a row reconciled merely because the local values look plausible.",
        "",
        "| # | Pre root ID | Post root ID | Local roles/sides | Local pair synapses | Neuropil rows | Codex direction/count | Lookup evidence | Result |",
        "| ---: | --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for index, pair in enumerate(checks, 1):
        role = f'{pair["pre_role"]} ({pair["pre_side"]}) → {pair["post_role"]} ({pair["post_side"]})'
        lines.append(
            f'| {index} | {pair["pre_root_id"]} | {pair["post_root_id"]} | {role} '
            f'| {pair["pair_synapses"]} | {pair["neuropil_rows"]} | pending | pending | pending |'
        )
    lines.extend([
        "",
        "## Reconciliation rule",
        "",
        "Mark a check as matched only after an independent Codex v783 view confirms",
        "the ordered pre→post pair and its displayed synapse total under an equivalent",
        "aggregation/filter. Document any portal mismatch rather than changing the raw",
        "count. The P1 gate stays open until all ten checks are documented or discrepancies",
        "are explained and resolved.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    source = root / "data/derived/ocellar_path_screen.json"
    report = json.loads(source.read_text(encoding="utf-8"))
    if not report.get("exploratory") or report["row_count_scanned"] != 16847997:
        raise ValueError("Expected completed exploratory v783 screen")
    checks = select_checks(report["candidate_pairs"])
    output = root / "docs/manual_connection_checks_v2.md"
    with output.open("x", encoding="utf-8") as stream:
        stream.write(worksheet(checks, "data/derived/ocellar_path_screen.json"))
    print(json.dumps({"output": str(output), "checks": len(checks), "status": "pending Codex review"}))


if __name__ == "__main__":
    main()
