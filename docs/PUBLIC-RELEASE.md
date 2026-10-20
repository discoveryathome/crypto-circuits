# Public release packaging

The owner authorized GitHub publication and a Discovery@Home hub listing on
2026-10-20. Repository visibility does not enable donor intake: `review.paused`
remains true, and no hub assessment grade is claimed.

The public repository starts from a clean snapshot of the locally committed
pilot (`c62cdf498b6279f12c3fe2e9eaaeb539e4a5e51b`), followed by the publication
packaging changes. The complete earlier Git history is retained locally,
outside the public repository. Historical commit IDs in experiment receipts
identify that local history; they are not promised to resolve on GitHub.

The public history excludes 64 upstream SBP files and 48 converted certificates
because their redistribution terms are unresolved. It retains the provenance,
expected hashes, fixed mathematical specifications, results and review records.
The original plans and their pinned inputs are not silently changed. A complete
verification requires restoring the omitted inputs with:

```sh
python3 tools/fetch_optional_artifacts.py
python3 research/agent-pilot-v2/tools/verify_results.py
```

The default fetch restores only the two files needed by the six-session agent
experiment. `--all` restores all 112 omitted files for the broader calibration.
The fetcher downloads pinned source data from the author's repository, checks
its SHA-256, and applies locally authored parsers to regenerate the converted
certificates. Every generated file must match its original recorded SHA-256.
No upstream program is executed, no checker is relaxed, and no cached verdict
substitutes for verification. If upstream retrieval fails or bytes change,
restoration fails rather than changing the experimental record.

Fetched files are ignored by Git. Do not force-add them or push the archived
local history. These packaging choices do not grant new rights over upstream
artifacts; see `THIRD-PARTY.md`.

The separate AES S-box pilot is not included in this repository. AES
MixColumns is included as one fixed linear-map instance.
