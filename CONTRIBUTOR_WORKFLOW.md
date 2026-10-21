# Contributor workflow — 21 October 2026

Start with `python3 tools/pick_task.py`. The ordinary draw includes concrete
Whirlwind M0/M1, Twofish, Joltik, Grostl and Whirlpool/Maelstrom tasks. AES S-box
work is optional and excluded from the routine draw. Field/design tracks remain.
The four additional linear maps are breadth probes, not promises of easy records.

```sh
python3 tools/task_context.py whirlwindm0
```

This checks the pinned specification and known circuit witnesses, combines the
original experiment, post-freeze prior and later agent findings, and emits the
nondominated known coordinates and count-only literature guards. Choose a starting
witness from that output. Equal coordinates already count as known even if the
circuit hash differs. Unresolved novelty does not make a valid circuit unknown.

If optional pinned artifacts are missing, run `python3 tools/fetch_optional_artifacts.py --all`.
This downloads hash-checked data and converts certificates; it does not execute
upstream code. Preserve those external artifacts' existing attribution terms.

Use a 30-minute initial session: 5 minutes orientation, 15–20 minutes bounded
search, and the remainder for two-checker verification and a receipt. Adapt the
existing optimizer or a small replacement window; no optimizer rewrite is required.

```sh
python3 -I tools/check_submission.py portfolio/INSTANCE.json CANDIDATE.json
python3 -I tools/audit_submission.py portfolio/INSTANCE.json CANDIDATE.json
```

Both commands must agree under the same binary-gate, port and depth model.
Correctness is not a novelty decision. Review all known Pareto points, missing-depth
claims, literature and component reuse before credit. The prior six-session screen
already includes independent-agent adjudication; external scientific review and
success across additional families remain unmeasured. Review only the final
nondominated outputs per session, retaining earlier checkpoints as provenance.

## Session receipt and review

Record the base commit, selected task and seed, input and output hashes, commands,
budget and elapsed time, successful and failed attempts, verification output,
and what remains unresolved. Check the live Handoffs Discussion before claiming
work. Post or open a focused PR only within the contributor's authorization.
A task draw is advisory; it does not reserve work.

A useful outcome can be a new witness, an independently checked result, a
source-backed correction, or a reproducible blocked handoff. Repeating a known
positive control is onboarding evidence. Review records must distinguish code
replay, independent implementation, scientific review and maintainer acceptance.

For the next monitored cohort, record cold-start orientation time, first useful
artifact, reviewer minutes, acceptance latency, duplicate work and unsuccessful
sessions. Later sessions inherit every known valid result. A lack of improvements
is evidence to revise the task pool, not a reason to reset it to weaker baselines.
