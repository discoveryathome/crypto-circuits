# Independently checking this experiment

Work from the repository root. No submitted executable code is needed.
The original experiment remains in `results/`; this experiment is separate.
The [fresh-checkout validation receipt](review/fresh-checkout-validation.json)
records a successful run from an archive of the committed package, including
reconstruction of the assessment and current frontier.

The public release needs a one-time fetch of pinned SBP data. The fetcher
regenerates the omitted certificate and requires its original hash; the frozen
plan and checker remain unchanged. Subsequent verification is offline.

```sh
python3 tools/fetch_optional_artifacts.py
python3 research/agent-pilot-v2/tools/verify_results.py
```

This checks the frozen plan digest, pinned tools and specifications, initial
comparator hashes, session frontier hashes, and the complete submission
inventory. It then freshly runs both trusted checker implementations on every
unique submitted certificate. It does not rely on cached success flags.
The printed timings describe this new verification run, not the original
review costs. A passing result proves the recorded functions and gate costs;
it does not decide novelty.

For one new submission, select the specification yourself:

```sh
python3 -I tools/check_submission.py portfolio/whirlwindm0.json /path/to/circuit.json
python3 -I tools/audit_submission.py portfolio/whirlwindm0.json /path/to/circuit.json
```

Use `portfolio/whirlwindm1.json` or `portfolio/square-aes-mugi.json` for the
other selected maps. Never accept a replacement specification from a submitter.
The files' expected hashes are in `plan.json`. Each certificate is a strict
acyclic straight-line program with only `inputs`, `gates`, and `outputs`.
Both checkers reject AND gates for these linear-map tasks. Exact affine
propagation and independent zero/basis evaluation therefore establish equality
on all possible inputs; random testing is unnecessary.

The full gate model is in `../../docs/VERIFICATION.md`. General submissions use
binary XOR, binary AND, NOT, and constants; NOT is charged, wiring and fanout
are free, and depth uses unit-delay gates. The four Pareto coordinates remain
AND, XOR, total gates, and depth. For the XOR-only circuits found here, AND=0
and total=XOR.

Review `preparation/literature/comparators.json`, the published source
provenance, the session's `all-known-prior.json`, and the final review records
before claiming a new construction. Missing published depths remain unresolved
comparators. Different hashes or same-cost circuits do not create discoveries.
Wave-two results must improve the already strengthened wave-two starting
frontier. Superseded checkpoints are evidence of the search, not independent
discoveries to add to a leaderboard.

## Running a fresh bounded search

The original local toolkit needs Python 3 and a C++17 compiler. Its source,
tests and method description are under `preparation/search/`.

```sh
python3 research/agent-pilot-v2/preparation/search/run_search.py \
  --spec portfolio/square-aes-mugi.json \
  --start certificates/square-aes-mugi--aes-mixcols-xor88-depth5-circ.json \
  --seed 12345 --cpu-seconds 30 --wall-seconds 60 \
  --output work/my-new-search
```

Use a new output directory, record a new seed and budget, and include the
current complete frontier as repeated `--start` arguments for a research run.
The example command illustrates the interface; beating its one start is not
enough for novelty. Whole-map synthesis can consume most of a short budget.
The actual sessions' original local method variants, commands, seeds, failures
and checkpoints are retained in `sessions/`.

Do not rerun expired `budget_run.py` session commands or write into the frozen
experiment. Reproduce an inner optimizer in a new experiment/output directory
after reviewing its local source. Wall-clock stopping can change how many
deterministic search steps finish. A fresh LLM session is not an exact replay
of an earlier model trajectory. Data-certificate verification is deterministic.

Everything is local. This checkout has no automated publication or donor intake.
