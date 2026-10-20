# Cryptographic circuit optimization

This pilot tests whether a portfolio of useful cryptographic circuit problems
can support recurring **new published-frontier advances**. It does not count
rediscovery, a better internal seed, a new matrix with old costs, or verification
work as a research discovery.

The portfolio contains **32 fixed instances**: 24 published linear maps, six
polynomial-basis binary-field multipliers, and two block-MDS diffusion-design
problems. It includes 59 frozen published baseline certificates, plus 47 later
SBP verification records and one derived-prior ARIA correction. The
complete AES S-box remains a separate high-ambition track in
a separate local pilot; it is not bundled here or included in this experiment's success denominator.
SHA-256, Keccak, Poseidon and full-cipher synthesis remain deferred.

**Latest result: [the actual-agent screening report](research/agent-pilot-v2/REPORT.md).**
Four of six capped agent sessions produced independently adjudicated advances
against the reconciled published frontier, with progress on both Whirlwind maps
in both waves. Both AES MixColumns sessions returned no new point. The frozen
screen passed for a larger private beta; public launch remains paused.

The [original launch assessment](docs/LAUNCH-ASSESSMENT.md) covers the earlier
seeded algorithm calibration, whose frozen results remain unchanged.
Code-independent checking and separate-agent review are not external scientific
review. The repository is being registered with the Discovery@Home hub; public
donor intake remains paused. Historical experiment reports retain their original
LOCAL-only execution status.

## Run locally

The public release omits SBP source artifacts and converted certificates whose
redistribution terms remain unresolved. Fetch pinned data and regenerate those
certificates locally before checking the complete historical experiment:

```sh
python3 tools/fetch_optional_artifacts.py
```

This downloads one source file and regenerates one certificate for the agent
experiment, checking both against their recorded SHA-256 hashes. Use `--all`
to restore the original calibration’s optional SBP inputs too. Downloaded data
is never executed and stays ignored by Git. See [public release notes](docs/PUBLIC-RELEASE.md).

Python 3.9+ and its standard library are sufficient for the original calibration
and certificate checking. After the optional inputs have been fetched, no
network connection or submitted executable is needed. The newer agent experiment's search methods additionally use C++17
and, for some unsuccessful AES attempts, an already installed Z3 solver;
see its [checking and search instructions](research/agent-pilot-v2/CHECKING.md).

```sh
python3 research/agent-pilot-v2/tools/verify_results.py
```

Original calibration commands:

```sh
python3 -m unittest discover -s tests -v
python3 -I tools/check_submission.py portfolio/joltik.json certificates/joltik--nist.json
python3 -I tools/audit_submission.py portfolio/joltik.json certificates/joltik--nist.json
python3 tools/check_all.py
python3 tools/replay_trial.py --instance joltik --wave 0
python3 tools/analyze_results.py
```

`check_all.py` rechecks the frozen sources and all archived results; field
multipliers dominate its run time. `--baselines-only` is a shorter check.
`replay_trial.py` reruns the recorded seed in a fresh temporary directory and
compares candidate hashes. Timing equality is not expected.

The original calibration outcome was **0 confirmed published advances**, with 15 of 70
corpus proposals rejected against checked prior and 55 still unresolved.
This is a short algorithm calibration, not a measured donated-agent discovery
rate. Its launch recommendation was to postpone; the later agent screen
supports a larger private beta while public launch remains paused.

```sh
# Resume any missing trials; complete receipts are left untouched.
python3 tools/run_benchmark.py
# Independently recheck every corpus proposal and one witness per instance.
python3 tools/analyze_results.py --audit
```

To reproduce the post-freeze literature corrections and adjudications:

```sh
python3 tools/audit_aria.py
python3 tools/audit_sbp.py
python3 tools/adjudicate.py
python3 tools/analyze_results.py
python3 tools/render_report.py
```

The SBP command can take several minutes on its first run because it performs
exhaustive scalar checks of each design certificate. Later runs reuse
certificate-hash-specific second-check receipts. To independently check any
individual certificate afresh, use `tools/audit_submission.py` directly.

The plan contains five waves of 32 trials, each independently seeded from OS
randomness. Seeds, work budgets, source hashes, starting circuits and a launch
decision rule were frozen before the first trial. New runs need a new plan and
separate receipts; never overwrite the recorded experiment.

## Navigate

- [Actual-agent experiment and decision](research/agent-pilot-v2/REPORT.md)
- [Current selected-map frontier](research/agent-pilot-v2/review/current-frontier.json)
- [Portfolio and baseline reconciliation](docs/PORTFOLIO.md)
- [Literature audit and limits](docs/LITERATURE.md)
- [Gate model and independent verification](docs/VERIFICATION.md)
- [Submission and novelty rules](docs/SUBMISSIONS.md)
- [Experimental design](docs/EXPERIMENT.md)
- [Fresh-checkout validation](docs/VALIDATION.md)
- [Agent entry point](AGENTS.md)
- [Machine-readable plan](results/plan.json), [summary](results/summary.json),
  [proposals](results/proposals.json), and [second checks](results/second-checks.json)

All metrics are reported separately. For linear maps, AND is fixed at zero;
XOR count and depth carry the tradeoff. For multipliers, AND, XOR, total gates
and depth remain separate Pareto axes. Constants and wiring are free; NOT is paid.
An XNOR or a three-input XOR must be expanded before comparison.

Source bytes are retained under `sources/`, with upstream licenses. See
[third-party notices](THIRD-PARTY.md). The original pilot code is MIT-licensed.
