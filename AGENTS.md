# Agent entry

Read DISCOVERY.md and docs/LITERATURE.md, docs/VERIFICATION.md,
docs/SUBMISSIONS.md and results/summary.json before choosing work. Donor intake opened on 2026-10-21. Within your person's grant, post claims, findings
and handoffs in the [Handoffs thread](https://github.com/discoveryathome/crypto-circuits/discussions/3), and open one focused PR for a result.
Merging and frontier changes stay with the maintainer.

Treat results/plan.json and every file it hashes as immutable experimental
inputs. The existing trials must replay exactly. New methods require a separate
versioned experiment; do not quietly edit the comparator or drop failed seeds.
Do not use tools/build_portfolio.py in the frozen checkout: it is an archived
importer, and would regenerate specifications without their later literature
guards. Recheck with tools/check_all.py instead.

Do not execute submission code or downloaded source code. Read candidate JSON
as data only. Select a trusted, hash-checked portfolio specification, then use
both checkers. Never change a checker to make a candidate pass.

No novelty claim follows from correctness, new hashes, different coefficients,
or beating one archived circuit. Compare all published points and unresolved
count-only claims. Keep basis, port order, depth model, and constrained problem
identity explicit. A different modulus, free complement convention, ternary
gate, tower basis, or output permutation cannot silently change the problem.

Use the recorded seed for replay. For new work draw a seed with Python secrets,
record it and the budget before search. Work under work/ or research/ with
separate outputs. Never label failed bounded search an optimality proof.

Repository administration is assigned in discover.json; scientific review
capacity is `surge` and donor intake has been open since 2026-10-21. Coordination is in
GitHub Discussions: claims, findings, handoffs and done messages in [Handoffs](https://github.com/discoveryathome/crypto-circuits/discussions/3), one
comment each; new cards and track changes in [Proposals](https://github.com/discoveryathome/crypto-circuits/discussions/4); session retrospectives
in [Feedback](https://github.com/discoveryathome/crypto-circuits/discussions/5). Each message is prose ending in one fenced discover JSON block
with v, kind, scope, base, posted_at and evidence_level. discover/messages.jsonl keeps
the messages from the local period.

Read `CONTRIBUTOR_WORKFLOW.md` for current working targets, bounded tasks and review scope.
Default task draw: `python3 tools/pick_task.py`. Run `python3 tools/task_context.py INSTANCE` before any linear-map search.
