# Frozen experiment

The plan was written before the first trial and hashed:

`c593e86b74eb5371c17c7336bc33be45a04e87f343b7a86d7507616d6388c34a`

It fixes all 32 problem specifications, 59 imported witnesses, source-code
hashes, 160 independent 128-bit OS-random seeds, five waves, starting-circuit
selection and work budgets. Each wave visits the same portfolio. Failed or
missing trials remain in the denominator; the runner supports resumption.

| Track | Budget per trial |
|---|---|
| Linear map | 32 randomized common-subexpression syntheses; 256 rewrite-walk steps |
| Binary-field multiplier | 256 exact-signal rewrite-walk steps |
| Diffusion design | 256 matrix draws; one synthesis per distinct MDS survivor; 256 rewrite-walk steps |

The fixed unit is work, not wall time. Dimensions and candidate-gate counts
change the cost of a unit; CPU and wall time are both recorded. Other work on
this shared machine causes wall/CPU divergence, so these timings are descriptive,
not isolated hardware performance measurements.

Randomized common-subexpression synthesis is cancellation-free. The walks
allow neutral earlier-signal resubstitution and single-fanout XOR reassociation,
with exact signal equality. They never accept a coordinatewise-worse state.
Multiplier signals use full truth tables. The design search samples circulant
and involutory Hadamard matrices over GF16 and screens all field minors before
synthesis. The verifier independently checks binary block ranks.

These are deliberately small, auditable search methods. They do not reproduce
the full BP/eBP, SAT-window, GPU, HILL, or structural multiplier search engines
in the literature. A negative result limits only this search configuration.
Each trial begins with a member of the frozen published corpus frontier,
round-robin across waves. Discoveries are not fed into later searches. Every
trial's retained Pareto candidates, including unchanged starting witnesses, are
independently checked and stored.

## Accounting

1. A correct candidate is an accepted function/cost certificate.
2. A candidate not dominated by the frozen imported witnesses is a **corpus
   proposal**. This can be an internal improvement or an unresolved Pareto point.
3. Chronological deduplication counts a new cost tuple only once per instance;
   a repeated hash or a different matrix at the same tuple does not count.
4. Published-frontier acceptance additionally requires the second checker and
   candidate-specific novelty adjudication with sources. Unknowns remain unknown.
   Missing published depths are never invented.

`results/novelty-audit.json` records acceptance, rejection or unresolved status.
Nothing is automatically accepted as novel by the benchmark. A change to the
published baseline discovered during adjudication is recorded separately from
the frozen trial comparator; it can invalidate a claim without rewriting history.

The operational screening threshold was at least five unique audited published
advances, on at least three instances, at least two in the final two waves,
with second checks under 60 seconds. Meeting that screen would still require
external review and actual donated-agent trials. Failing it recommends postponing
the cryptography launch, as requested.

No iid confidence interval is reported: repeated instances and common methods
create dependence. The rate of **confirmed** advances is not an estimate of
all unknown true novelty. Unresolved proposals are reported separately.
Actual donated agents, token costs, human review time and long-term saturation
have not been measured. A positive calibration would justify a second stage:
fixed 30–60 minute agent sessions with fixed model/token budgets, the same
frozen specifications, candidate-specific literature checks and blinded external
verification. This session does not substitute synthetic trials for those agents.
