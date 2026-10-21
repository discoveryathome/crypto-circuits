# Readiness assessment — crypto-circuits — 21 October 2026

Recommendation: **Lead candidate for a monitored beta**.

The two-wave screen already demonstrates inherited-frontier progress on two related Whirlwind maps. The old catalogue still centered broad algorithm work and did not expose those working targets or concrete breadth tasks.

## Completed changes

- Added six concrete linear-map tasks, a seeded picker and a context command that combines published baselines, original trial candidates, post-freeze prior and later agent results.
- The context command retains unresolved literature guards and all known nondominated coordinates. The six maps passed both checker implementations.
- Removed AES S-box work from the ordinary draw and retained it as explicit optional work; clarified the existing intake decision without claiming scientific acceptance.

## Validation

10 existing tests; 391 original/post-freeze certificate checks; all 147 agent submissions rechecked with both implementations; six task contexts independently evaluated by the second checker; 120 seeded picker draws and invalid-seed rejection; current schema validation.

All 10 active task cards' first-step commands passed; repeated identical commands were cached within the check.
Executed outputs are in [checks/](checks/). This is coordinator review and replay,
not an independent cold contributor study or external scientific signoff. No new
research-success rate is inferred. Current workflow: [CONTRIBUTOR_WORKFLOW.md](../../CONTRIBUTOR_WORKFLOW.md).

## Next scientific handoff

External scientific review of Whirlwind equivalence, cost model, component reuse and literature comparisons, followed by cold contributor sessions on additional cipher families. The added maps have known witnesses, not established sustained donor yield.

Acceptance test: A scoped external verdict for the 156-XOR M0 and 163-XOR M1 constructions plus all relevant count/depth tradeoffs; explicit unresolved comparators; then nonduplicative outcomes measured across additional maps.

```sh
python3 tools/fetch_optional_artifacts.py --all
python3 research/agent-pilot-v2/tools/verify_results.py
python3 tools/task_context.py whirlwindm0
python3 tools/task_context.py whirlwindm1
```

## Integration state

Base: `ba722e92311ab59580a5d239a093c9186d849b1a`. Remote main at fetch: `0cb2af3fb11a7ac07629132cbd2c657c5e3a4ac6`.
This work builds on the newer local launch/coordination branch. The existing
[launch PR #1](https://github.com/discoveryathome/crypto-circuits/pull/1) was still open when
checked, and its Handoffs thread had no comments. Local launch decisions are not
proof that remote main or the public launcher has adopted them. No remote write,
merge, announcement, scientific acceptance or observation submission occurred.
