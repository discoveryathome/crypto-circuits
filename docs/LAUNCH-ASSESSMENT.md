# Launch assessment — 2026-10-20

**Recommendation: postpone the cryptography launch.** This pilot has not demonstrated a sustained stream of independently established new published-frontier results. The local software and experiment are complete; the scientific launch criterion is unmet.

This is a preliminary calibration of small search algorithms, not an evaluation of actual donated LLM-agent sessions. It neither proves that cryptographic optimization is exhausted nor establishes a true zero discovery rate. Unresolved novelty remains unresolved.

## Measured outcome

| Quantity | Result |
|---|---:|
| Fixed useful instances | 32: 24 linear maps, 6 multipliers, 2 MDS-design problems |
| Frozen published baseline certificates | 59 |
| Completed seeded algorithm trials | 160/160; no missing trials |
| Trials improving the imported corpus | 128/160 (80%) |
| Chronologically unique corpus Pareto proposals | 70 |
| Proposals matched or dominated by checked prior | 15 |
| Proposals with unresolved published-frontier novelty | 55 |
| Confirmed published-frontier advances | 0 |
| Actual donated-agent sessions / external novelty reviewers | 0 / 0 |
| Search CPU / sum of per-trial wall time | 189.41 s / 384.05 s |
| Primary checking of all 284 retained trial certificates | 20.08 s |
| Second-check process time, 70 proposals: median / max | 0.090 s / 8.357 s |
| Second checks: 70 proposals plus 32 baseline controls | 102 successful; 64.20 s total |

The 0/160 rate is the rate of **confirmed** advances in this bounded experiment. It is not an estimate of true novelty among unresolved proposals. Functional verification succeeded for all proposals. The second checker was implemented separately but by the same local author; no external review is implied. Human literature-review time and donated-agent token/time costs were not measured. Additional post-freeze prior checks are recorded separately and excluded from these experimental checking-time totals.

| Wave (32 trials each) | Internal-advance trials | New corpus proposals | Confirmed published advances |
|---|---:|---:|---:|
| 1 | 25 | 39 | 0 |
| 2 | 25 | 11 | 0 |
| 3 | 25 | 7 | 0 |
| 4 | 26 | 9 | 0 |
| 5 | 27 | 4 | 0 |

The five waves used independent OS-random seeds and fixed work budgets. They always began from the frozen published corpus, not newly found circuits. Chronological deduplication prevents repeated rediscoveries or new matrices at old coordinates from looking like sustained progress. No independence-based confidence interval is justified. Wall timings were affected by concurrent work on the machine.

## What the literature reconciliation changed

The imported corpus was sourced from publications, not deliberately weakened. Nevertheless, a published archive is not the current frontier. Current NIST AES MixColumns witnesses, Xu–Sun's circulant constructions, Jain's released polynomial multipliers, and count-only claims stronger than available witnesses were included before search. Post-search SBP imports removed more apparent wins.

- Four small cipher-map depth improvements are already present in the released SBP results. Published shallow MDS designs also eliminate several design proposals. The exact rejected hashes and dominating witnesses are recorded in the novelty audit.

- ARIA's apparent 387→386 XOR reduction loses to a 384-XOR, depth-5 construction obtained by copying a 48-gate bit-plane already in the published artifact. That is a baseline correction, not a credited discovery.

- No trial reduced the best imported multiplier AND count or established a new published minimum-XOR record. The remaining proposals concern depth tradeoffs or incomplete prior comparisons.

- Quantum CNOT depth, mixed-fan-in gate counts, hardware GE, and free basis changes are not silently compared against binary-XOR SLP metrics.

See [LITERATURE.md](LITERATURE.md) for primary references, precise access and normalization gaps, and the [per-candidate adjudications](../results/novelty-audit.json).

## A verified transformation

The GF(2^5), modulus 0x25 trial in wave 4 preserves 20 ANDs, 24 XORs and 44 total gates while reducing depth from 6 to 5. The complete 1024-input multiplication table passes both checkers. This demonstrates a real equivalent transformation; its published novelty is unresolved.

```sh
python3 -I tools/check_submission.py portfolio/gf5-25.json results/candidates/w3-gf5-25-0.json
python3 -I tools/audit_submission.py portfolio/gf5-25.json results/candidates/w3-gf5-25-0.json
```

## Decision and next evidence

The preregistered screen required at least five audited new published points on at least three instances, including two in the last two waves, with second checks under 60 seconds. Correctness cost passed comfortably; demonstrated novelty did not. The screen was an operational choice, not a statistical theorem or a promised donor rate.

Keep intake paused. First close the candidate-specific literature gaps and obtain external review. If continuing internal research, test cancellation-aware linear synthesis, structural multiplier decompositions, or bounded exact replacement in a new frozen experiment. The present cancellation-free synthesis and small rewrite walks used only about three CPU minutes of search in total, so they cannot rule out stronger methods. Only after promising audited yield should a separately authorized study measure fixed-budget real agent sessions and actual review costs. AES S-box synthesis remains a stretch track.

The [task catalogue](../discover/catalog.json) records that research backlog. No remote repository, publication, messages, hub registration or donor intake was created. The manifest deliberately has no invented maintainer and is not eligible for public registration.
