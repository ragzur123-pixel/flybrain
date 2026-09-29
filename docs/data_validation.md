# P1 raw-data validation — archive passed local scan; current Codex comparison failed, 2026-09-26

Selected lineage: FAFB v783, Zenodo record 10676866 and annotation tag `v2.1.0`. Raw products and local SHA-256 values are in `data/raw/manifest.csv`; source URLs, expected bytes, and published checksums are in `configs/data_sources.json`. The three original core downloads and the later presynaptic aggregate matched their published byte counts and MD5 or Git-blob SHA-1 identifiers. The manifest is rehashed before checks. Raw files are ignored by Git, while the manifest is available for versioning.

## Observed schemas and coverage

| Product | Observed facts | Limit |
| --- | --- | --- |
| `proofread_root_ids_783.npy` | NumPy shape `(139255,)`, dtype `uint64`; memory-mapped read | Membership array, not a connection table |
| Annotation `v2.1.0` TSV | UTF-8 tab-separated; 27 header columns including `root_id`, `flow`, `super_class`, `cell_class`, `cell_sub_class`, `cell_type`, `hemibrain_type`, `top_nt`, `top_nt_conf`, `side`, `status`; 139,255 rows, no duplicate/missing root IDs; all 139,255 IDs found in the proofread array | Labels and transmitter predictions are annotations, not proof of function or physiological sign |
| `proofread_connections_783.feather` | Arrow IPC/Feather v2 file, 258 record batches and 16,847,997 rows. Columns: `pre_pt_root_id:int64`, `post_pt_root_id:int64`, `neuropil:string`, `syn_count:int64`, and six neurotransmitter probability averages (`gaba_avg`, `ach_avg`, `glut_avg`, `oct_avg`, `ser_avg`, `da_avg`) as `double` | One pair can occupy multiple neuropil rows; pair aggregation and threshold policy are not frozen |

The first **three** connection batches contain 196,608 rows. In this bounded sample, `syn_count` ranged from 1 to 1,055; no pre/post ID or neuropil nulls, nonpositive synapse counts, self-loops, or IDs missing from the proofread array were found. Each of the six neurotransmitter-average columns had **37 nulls** in the sample. These are sample findings, not full-file rates. The machine-readable sample report is `data/derived/validation_report.json` and is intentionally excluded from Git as a generated artifact.

## Full automated scan

`src/flyai/validate_raw.py` rehashed all four current manifest entries, checked the annotation-to-proofread ID join, and scanned all 258 Arrow batches. Its generated report is `data/derived/full_validation.json` (ignored by Git). It found **16,847,997 connection rows**, total `syn_count` **54,492,922**, with range **1–2,405**. All required ID, neuropil, and count fields had zero nulls. There were zero self-loops, nonpositive counts, pre/post IDs absent from the proofread array, and exact duplicate `(pre, post, neuropil)` rows. Each of the six neurotransmitter probability columns had **1,732 nulls**. Missing probabilities need an explicit rule before using them as signs.

The scan finished in 157.64 seconds, with peak process RSS **1,007,906,816 bytes** and peak SQLite scratch **515,325,952 bytes**, below the 4 GiB process and scratch caps in `configs/resources.yaml`. These are data-integrity observations, not a manual Codex reconciliation or a sign inference. The archive's row-level minimum of one does not establish a five-synapse filter in the file.

After adding the auxiliary presynaptic aggregate, the full validator was rerun
on 2026-09-26. It rehashed **all four** manifest products and again completed
the 16,847,997-row graph scan with zero exact duplicate pair/neuropil rows.
The refreshed `full_validation.json` includes all four SHA-256 values;
this run took 159.06 seconds and peaked at 1,013,555,200 RSS bytes.

## Exploratory directed path screen

`src/flyai/screen_ocellar.py` scanned all 16,847,997 rows and found 958 distinct directed pairs among the 291 annotated candidate IDs, now including paired DNp22. It sums `syn_count` across rows for each ordered pair, then separately checks direct photoreceptor → descending paths and two-hop photoreceptor → OCG01 → descending paths at exploratory pair thresholds 1 and 5. The complete generated result is `data/derived/ocellar_path_screen.json`.

At threshold 5, left/right DNp28 each receive **direct** input from 18/31 distinct candidate photoreceptors; across all direct pairs, the raw file has 259/392 synapses on the respective sides. Their OCG01-mediated two-hop count is zero at five: OCG01 → DNp28 rows total only one synapse on the left and three on the right. This does **not** mean the DNp28 route is absent. It is a different, direct anatomical route. Right DNp28 is flagged `outlier_seg`.

At the same threshold, left/right DNp20 receive four/five OCG01 inputs and are reachable from 53/64 distinct photoreceptors through those intermediates. Left/right DNp22 receive four/five OCG01 inputs and are reachable from 54/78 photoreceptors. The primary paper distinguishes direct DNp28 from strong downstream OCG01 targets DNp20/DNOVS1 and DNp22/DNOVS2 (FW-050). These are candidate routes for further audit, not frozen outputs or proven steering commands. The screening thresholds are exploratory and not a protocol choice.

**2026-09-28 laterality correction:** Those 53/64 and 54/78 totals pool
photoreceptors from both biological sides and center. A reproducible recount
of the saved candidate pairs (`docs/ocellar_laterality_audit.md`; FW-061)
shows fully same-side two-hop unique-photoreceptor counts of 7/31 for
left/right DNp20 and 8/29 for left/right DNp22 at the same exploratory
threshold. These counts are not path counts or measured lateralized function.

## Independent archive-family aggregate check — 2026-09-26

The same [Zenodo v783.0 release](https://zenodo.org/records/10676866) provides a
separate `per_neuron_neuropil_count_pre_783.feather` summary of the full
synapse table (FW-055). Its published size and MD5 passed acquisition checks;
the local SHA-256 is `35442a46f076892dff91bd6e55fa1489b3acc64fda1d35cee7dbbbbc509a3dff`.
The observed schema is `pre_pt_root_id:int64`, `neuropil:string`,
`count:int64`, with 2,781,037 rows in 43 Arrow batches. This is an auxiliary
validation product, not a replacement for the directed edge list.

`src/flyai/check_archive_aggregate.py` rehashed all four raw products and
scanned the full graph and aggregate for the 19 IDs selected before portal
comparison. For each matching neuron and named neuropil, the proofread-partner
edge subtotal should be no larger than the full-synapse aggregate. **All 56
comparable neuron/region rows obeyed this bound.** The aggregate has 79
neuropil names and no `UNASGD` rows anywhere; two selected graph rows have
one synapse each in `UNASGD` and are explicitly **not comparable**. Their
absence is an observed product-coverage difference, not a zero-synapse claim.
The machine-readable 58-row result and both source hashes are in
`data/derived/archive_aggregate_check.json`. This cross-check supports
archive-family consistency but does not prove exact pair counts or reconcile
the ten current Codex differences. Why `UNASGD` is omitted is unverified.
None of the ten preselected pair rows uses `UNASGD` (checked against
`manual_pair_raw_audit.json`).

## Independent raw-row audit of manual-check pairs — 2026-09-26

`src/flyai/audit_manual_pairs.py` rehashed the four pinned manifest products and
independently rescanned all **16,847,997** connection rows for the ten ordered pairs
in `docs/manual_connection_checks_v2.md`, also retaining each reverse direction.
All ten forward synapse totals and neuropil-row counts agreed with the earlier
exploratory screen. The exact per-neuropil rows, reverse counts, source SHA-256,
and `portal_verified=false` are in the generated
`data/derived/manual_pair_raw_audit.json`. Six photoreceptor-origin pairs had
zero reverse synapses in the file. The four OCG01→descending pairs had reverse
counts **10, 18, 2, and 1**, respectively. A reverse count does not reduce the
forward count. `figures/manual_pair_audit.svg` and `.png` visualize these local
observations and mark all portal checks pending. This does not close P1.

**2026-09-26 correction:** that chart is an archive-only historical preview.
All ten current Codex portal exports are now checked and all ten counts differ.
See `docs/codex_reconciliation.md` and the current preview
`figures/codex_reconciliation.png`. Do not use the archive-only figure as a
portal-verified circuit result.

The ten pairs use 19 unique root IDs. `src/flyai/prepare_id_packet.py`
rehashes the pinned products, joins those IDs to the v2.1.0 annotation TSV
and the proofread-root array, verifies their roles/sides against the audit,
and writes `docs/candidate_id_packet.md`. All 19 passed these local provenance
checks. This is a provisional packet for later circuit review, not a selected
subnetwork or a replacement for independent portal validation.

## Candidate class observations, not circuit selection

The actual annotation TSV has 273 rows with `cell_type=ocellar retinula cell` (100 left, 97 right, 76 center), 12 OCG01 cells (6 left, 6 right), and two each of DNp20, DNp22, and DNp28 (one per side). DNp20/DNp28 appears in `hemibrain_type`, whereas DNp22 is in `cell_type`; a parser looking only at one field would omit a primary-paper candidate. The right DNp28 row has `status=outlier_seg`, which the annotation supplement defines as a segmentation-issue flag (FW-048); do not treat it as a clean symmetric output without review. The paper reports that released `side` labels already reflect the fly's biological left/right despite an imaging-axis inversion (FW-049). These IDs matched the proofread-ID array and were included in the exploratory screen. Selected circuit IDs belong in a later predeclared file after graph checks; none is frozen here.

## Reproduction and remaining checks

- Runtime for this inspection: project `.venv` with `numpy==2.5.3`, `pyarrow==25.0.1`, and `psutil==7.2.2` (`requirements-data.txt`); the downloader and its four `unittest` checks use the bundled Python standard library.
- Acquisition command: `.venv` or bundled Python running `src/flyai/acquire.py --workspace <workspace> --product <configured product>`, once per product. The downloader streams 1 MiB chunks, refuses overwrites, enforces published size and free-disk floor, checks MD5 or Git-blob SHA-1, and writes a manifest row with SHA-256 only after success.
- The annotation and bounded connection inspection was run with Python `csv`, NumPy memory mapping, and `pyarrow.ipc.open_file` over a memory-mapped Feather file. The exact results are saved in the generated JSON report and summarized above.
- Validation command: `.venv\Scripts\python.exe src/flyai/validate_raw.py --workspace <workspace>`; exploratory path command: `.venv\Scripts\python.exe src/flyai/screen_ocellar.py --workspace <workspace>`. Both exited 0 on 2026-09-25. The current full suite passed 12 tests on 2026-09-26 via `.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -v`.
- Independent audit command: `.venv\Scripts\python.exe src/flyai/audit_manual_pairs.py --workspace .` (exit 0, ten checks, 16,847,997 rows); preview command: `.venv\Scripts\python.exe src/flyai/render_pair_audit.py --workspace .` (exit 0). The SVG was converted to PNG with the bundled Node `sharp` package; both visuals were checked after render.
- ID packet command: `.venv\Scripts\python.exe src/flyai/prepare_id_packet.py --workspace .` (exit 0, 19 IDs).
- A revised ten-pair packet covering direct and two-hop routes is in `docs/manual_connection_checks_v2.md`; the original `docs/manual_connection_checks.md` is retained as an earlier draft. The 2026-09-25 browser session showed sign-in and no lookup was asserted then. On 2026-09-26 the v783 Cell Details pages were accessible, and ten hashed CSV exports were saved locally. `src/flyai/reconcile_codex_exports.py --workspace .` found **0 matched, 10 discrepant** counts; exact rows and hashes are in `docs/codex_reconciliation.md` and `data/derived/`.
- Archive-family check command: `.venv\Scripts\python.exe src/flyai/check_archive_aggregate.py --workspace .` (exit 0; 19 IDs; 56 comparable rows; two `UNASGD` rows not comparable). The synthetic subset-bound test is in `tests/test_check_archive_aggregate.py`.
- Historical 2026-09-26 next step: resolve the archive-versus-current-Codex product difference before selecting circuit IDs or thresholds. The gate failed under the earlier cross-product rule. **2026-09-28 update:** Rüzgar selected the 2024 archive; a fresh full scan, ten raw pair audits, and the qualified aggregate check passed the [archive-specific P1 gate](p1_archive_gate_review_2026-09-28.md). Current Codex differences remain a separately disclosed product comparison.
