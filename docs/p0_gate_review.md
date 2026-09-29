# P0 gate review — 2026-09-25

**Decision: pass for a local, noncommercial research workflow.** This gate permits selecting and validating public data. It does not certify biological function, competition eligibility, commercial use, redistribution of source data, or the final report.

| Gate condition | Evidence | Result |
| --- | --- | --- |
| Critical factual claims have source locations or are marked unverified | `docs/claim_audit.md`; source ledger plus unresolved circuit IDs, model mapping, and novelty issues | Pass |
| Necessary data use and derived reporting are permitted | FlyWire v783 public-release guideline says CC BY-NC 4.0 and includes proofreading/annotations (FW-007); official Zenodo v783 archive says CC BY 4.0/open (FW-035); both allow noncommercial attributed reuse and adaptation (FW-008). The author's annotation repository links this archive and tag v2.1.0 is v783 (FW-034). Apply the stricter noncommercial terms to local data and report figures; no source-file redistribution. | Pass for this restricted use |
| Competition requirements and open model/source questions recorded | Official 2026–2027 call and guide (FW-021–FW-024, FW-043), template (FW-032–FW-033), and `docs/issues.md` | Pass as a recorded-requirements check; eligibility, field submission, and design-specific permissions still need review |

The empty license display on Zenodo and absent repository license file are disclosed in `docs/data_candidate.md` (FW-031, FW-038). They do not erase the positive FlyWire v783 public-release guidance, but require caution for any redistribution. The authenticated Codex portal is not needed for the official Zenodo/archive route. Actual file hashes, schemas, joins, circuit IDs, threshold policy, and neuroscience interpretations belong to P1/P2.

The E03 supplement review, E06 comparable-work search, and competition details continue as open work and must be finished before final claims. This gate should be revisited if a chosen product, use, or release changes.
