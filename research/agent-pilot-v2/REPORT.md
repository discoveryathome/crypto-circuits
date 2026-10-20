# Actual-agent screening result — 2026-10-20

**The frozen screen passed: proceed to a larger private beta. Public launch
remains paused.** Four of six actual agent sessions advanced the reconciled
published frontier under independent-agent literature review. Both Whirlwind
instances improved in both waves; neither AES MixColumns session produced a
new point. This is encouraging evidence of repeatable progress on these tasks,
not an estimate of the success probability for arbitrary contributors or the
whole 32-instance portfolio.

## Constructions

Pairs below are `(binary XOR gates, classical depth)`. AND=NOT=0 and total=XOR.
The full current frontier, provenance and unresolved count-only comparisons
are in [current-frontier.json](review/current-frontier.json).

| Fixed map | Retrieved published frontier | Accepted wave-one frontier | Accepted wave-two frontier |
|---|---|---|---|
| AES MixColumns | `(88,5), (90,4), (97,3)` | No advance | No advance |
| Whirlwind M0 | `(159,14)` | `(157,12), (161,11), (163,10), (170,9)` | **`(156,12), (157,11), (158,10), (166,9)`** |
| Whirlwind M1 | `(169,11)` | `(166,10)` | **`(163,10), (164,9)`** |

The Whirlwind published witnesses come from
[Xu and Sun's May 2026 revision](https://arxiv.org/html/2511.18226v2)
and its pinned artifacts. Their in-place XOR instructions were converted to
straight-line programs without changing count; the classical depths above
were recomputed locally. These results do not claim improved in-place
circuits or quantum schedules. The AES witnesses come from the
[NIST circuit catalogue](https://csrc.nist.gov/projects/circuit-complexity/list-of-circuits),
with exact hashes and source attribution in the preparation audit.

The smallest counts fell from 159 to 157 to 156 for M0, and from 169 to 166
to 163 for M1. The other points preserve useful count/depth tradeoffs.
No weighted score combines these coordinates.

There were **11 accepted session-end frontier advances across the two waves**,
but only **six accepted points survive on the final combined frontier**:
wave two dominates all five accepted wave-one points. These are related
constructions, not eleven independent scientific breakthroughs.

All **147 submitted certificates passed both checker implementations**.
Independent review considered the 18 surviving per-session frontier points:
11 were accepted and seven remained unresolved. The other 129 certificates
are superseded checkpoints and receive no separate discovery credit.
Six unresolved points survive after wave two: M0 `(205,8), (206,7), (210,6),
(214,5)` and M1 `(215,6), (224,5)`. Known published circuits with missing
classical depths could dominate these; they receive zero credit.

## What was measured

The [plan](plan.json) was frozen before search, at local commit
`3e5b0ef72daf9079e33360d8ef3d31103770aabe`. Its SHA-256 is
`e13c95221645d66df1ba36c59df662d3dbb4e8b0ae82dcce8045911a339b0097`.
Six fresh agent contexts received independently recorded search seeds and
1,200-second elapsed caps, in two waves of three. Time includes dispatch,
setup, reasoning, implementation, compilation, search and self-checking.
Searches adapted within those caps. Seeds control search tools, not model
sampling.

Every correct prior local construction was already ineligible for credit.
Wave two received all verified first-wave candidates as known prior,
including unresolved ones. The M0 wave-one start was already stronger in
classical depth than its published size witness. These were not deliberately
weak baselines. No failed session or seed was removed from the denominator.

| Session | First provisional submission | First subsequently credited final witness submitted | Accepted session-end points |
|---|---:|---:|---:|
| Wave 1 AES MixColumns | None | None | 0 |
| Wave 1 M0 | 4.7 min | 4.8 min | 4 |
| Wave 1 M1 | 6.3 min | 10.7 min | 1 |
| Wave 2 AES MixColumns | None | None | 0 |
| Wave 2 M0 | 3.7 min | 7.5 min | 4 |
| Wave 2 M1 | 8.0 min | 12.4 min | 2 |

These are submission latencies from the issued clock, not literature-acceptance
times. Novelty review was batched after each wave, completing at 06:55:28 UTC
and 07:19:11 UTC. Earlier superseded candidates and first checkpoint times
are retained in the session receipts.

The successful methods used semantic identities, associative rewriting,
bounded resynthesis, circuit transposition, matrix symmetries, and selection
among shared intermediate representations. The reviewers checked that accepted
constructions changed computation graphs beyond numbering, dead-code removal,
representation conversion or simple scheduling. Established identities can
produce a new construction; no new optimizer theory is claimed.

AES used several additional approaches, including bounded SMT replacement
and finite-universe SAT extraction. None improved its frontier. Timeouts and
window-limited UNSAT answers do not establish global optimality.

## Verification, review cost and deviations

Both checkers reject nonlinear AND gates for this fixed linear-map profile.
One proves exact affine coefficient equality; the other independently checks
zero and every basis input after enforcing linearity. Consequently acceptance
proves equality on all inputs, not just sampled inputs. Circuit structure,
references, output order and costs are checked independently.

Root-side first verification of all 147 submissions took **21.84 seconds**
including process startup: median **0.142 seconds per certificate**, maximum
**0.256 seconds** on the shared host. A fresh final run of all 294 checker
processes took **12.35 seconds** after search stopped. These are separate
measurements, not contradictory estimates or additive discovery costs.

Independent novelty review took **206.33 seconds for wave one** and
**174.05 seconds for wave two**, about **6.34 minutes total**, after the
baseline corpus had been prepared. Mechanical per-point times are recorded;
shared literature effort is not artificially assigned to individual points.
Preparation and root coordination active time were not separately measured.
Model/token costs and exact model version are unavailable.

The aggregate issued-clock interval through observed search stops was
**7,144.18 seconds (119.07 agent-minutes)** against a 7,200-second cap.
Including receipt cleanup it was **7,239.57 seconds (120.66 minutes)**.
The first issue through the last receipt took **45.11 wall-clock minutes**,
including inter-wave review; preparation and final review are additional.

All executed searches stopped before their deadlines, apart from a 0.026-second
supervisor shutdown delay within its two-second grace. Administrative receipt
cleanup exceeded three deadlines by 24.724, 24.474 and 4.982 seconds. One
post-deadline balancing command was rejected before execution. One initial M0
seed was mistyped; its unsuccessful attempt was retained without resetting
the clock, and successful runs used the documented correct derivations.
One forced shutdown lost final child CPU accounting, so aggregate actual CPU
cost is **unknown**, not the raw sum of incomplete receipts.
[costs.json](review/costs.json) retains these distinctions.

## Decision and limits

The predeclared requirement was at least two accepted new points on two
instances, including one first found in wave two. The
[machine-readable assessment](review/assessment.json) applies that rule and
passes it. No threshold was weakened after seeing the results.

The next step should be a larger private beta across more cipher families in
the existing portfolio, followed by the multiplier and diffusion-design tracks.
Freeze updated literature baselines first, measure model costs and review
capacity, and test duplicate handling when several contributors attack the
same instance concurrently. Keep AES as an ambitious optional track.

This six-session, three-map sample is correlated; M0 and M1 are related.
The separate reviewer belongs to the same model family as the search agents.
Acceptance is against the reconciled identified literature, not proof that
no unpublished or unindexed construction exists. External scientific review
and a consenting maintainer with review capacity remain outstanding. The
experiment does not establish sustained yield across 20–40 tasks or justify
public donor promises.

## Inspect and reproduce

- [Independent checking and local search instructions](CHECKING.md)
- [Wave-one review](review/WAVE1-REVIEW.md) and [wave-two review](review/WAVE2-REVIEW.md)
- [Initial literature reconciliation](preparation/literature/AUDIT.md)
- [Sources and attribution](ATTRIBUTION.md)
- [Full verification ledger](review/checks.json) and [session records](sessions/)

The verification ledger preserves intake-time status; final novelty verdicts
are in the two adjudication packets and `assessment.json`.

A [fresh-checkout validation](review/fresh-checkout-validation.json) of commit
`f198e78c475ffa9d8ebacdf62a451cc6e05982e8` checked all 147 certificates with
294 checker processes in 23.22 seconds. Reconstructing the assessment matched
exactly apart from its generation timestamp, and the current frontier matched
byte for byte. No upstream or submission code was executed.

From the repository root:

```sh
python3 research/agent-pilot-v2/tools/verify_results.py
python3 research/agent-pilot-v2/tools/summarize.py
python3 research/agent-pilot-v2/tools/assess.py
```

The first command freshly checks hashes and every certificate as data. The
other two reconstruct observations and the screening decision from saved
receipts and reviewer verdicts. The original 32-instance algorithm experiment
and all its frozen inputs remain unchanged. No remote publication, author
contact, push, or donor intake occurred.
