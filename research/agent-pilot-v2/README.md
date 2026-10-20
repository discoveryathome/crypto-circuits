# Private agent-session screening experiment

This is a separate experiment. The original 160 algorithm trials, source
hashes, and adjudications are unchanged. The user authorized six independently
seeded, 20-minute agent sessions in two waves across three useful linear maps.
Everything remains local. Preparation and review time are outside the search
budget and are reported separately.

The selected instances are AES MixColumns (`square-aes-mugi`) and Whirlwind
M0/M1. They have current released binary-XOR witnesses. Selection was based
on useful fixed functions and available comparable artifacts, not on trying
candidate searches and keeping successful instances.

Each wave has one fresh agent context per instance. Each session has a
1,200-second elapsed-time cap, including its reasoning, implementation, search,
and self-checking. Three sessions may run concurrently. The total cap is two
aggregate agent-hours, approximately forty minutes of elapsed session time.
Preparation, coordination and independent review are additional costs.
Early termination is recorded honestly; agents must not idle to fill a budget.
Seeds control the search tools, not the underlying language-model sampler.
No statistical independence of outcomes is assumed.

## Frozen decisions

The machine-readable plan is written after baseline preparation and before
the first search session. It pins specifications, checkers, the initial toolkit,
all starting witnesses, seeds, session caps, gate models and acceptance rules.
Agents may develop their own methods inside their assigned session directory.
They may not edit the plan, trusted checkers, specifications or other sessions.
They cannot execute upstream downloaded code. Submitted circuits are data.

All correct earlier local candidates are known prior, even where their
published novelty remains unresolved. Rediscovering them earns no credit.
Wave 2 receives verified wave-1 candidates as additional known prior and
starting circuits. Published novelty is tracked separately from correctness.

The screening threshold is at least **two confirmed new Pareto points on two
different instances**, including **one first discovered in wave 2**. Every
credited point must pass both checker implementations and candidate-specific
literature review by an agent other than its search author. Correct circuits
with unresolved comparators earn no discovery credit. Missing-depth claims
cannot be silently ignored; exact blocker rules are retained with each case.

This threshold only justifies a larger private beta. It does not authorize
launch, establish long-term yield, or replace external scientific review.
One confirmed point warrants further investigation. Zero keeps launch paused.
The two-hour screening threshold is not retroactively applied to the original
160-trial experiment.

## Recorded evidence

For each session record actual start/end times, seed, agent identity, initial
frontier hash, source changes, submitted certificate hashes, search process
CPU/wall time, duplicates, invalid submissions, and stop reason. Model/token
cost is recorded only if the orchestration interface exposes it; unavailable
costs are not fabricated.

For each candidate separately record function and cost verification, source
comparison, prior dominance, duplicate status, novelty verdict, and reviewer
time. Time to first submission and time to adjudicated discovery are distinct.
Results remain unresolved if review is incomplete at the search deadline.

Repeated findings count once. The second wave tests whether progress continues
after newly verified constructions become known. The small sample supports a
screening decision, not a precise population success probability.
