#!/usr/bin/env python3
"""Render measured reports from receipts and explicit novelty adjudications."""
import collections
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT/path).read_text())


def point(m):
    return "/".join(str(m[k]) for k in ("AND", "XOR", "total", "depth"))


def main():
    summary = read("results/summary.json")
    proposals = read("results/proposals.json")
    checks = read("results/second-checks.json")
    prior = read("results/post-freeze-prior.json")
    plan = read("results/plan.json")
    specs = {r["id"]: read("portfolio/"+r["id"]+".json") for r in plan["instances"]}
    statuses = collections.Counter(p["novelty_audit"]["status"] for p in proposals)
    times = [checks[p["instance"]+":"+p["sha256"]]["process_wall_seconds"] for p in proposals]
    corpus = []
    lines = [
        "# Fixed portfolio and reconciled evidence\n",
        "Every tuple below is **AND / XOR / total gates / depth**. NOT is paid; "
        "constants and wiring are free. Complete coordinates come from checked "
        "certificates. Count-only claims remain separate. This is an audited "
        "artifact frontier, not a guarantee of exhaustive worldwide coverage.\n",
        "The 59 initial witnesses and specifications were frozen before search. "
        "Later SBP imports and the direct ARIA derivation are separate prior guards; "
        "they cannot be counted as search discoveries. See [the literature audit](LITERATURE.md).\n",
        "| Fixed instance | Profile / inputs | Frozen published witness tuples | Additional published XOR guard | Post-freeze checked prior tuples |",
        "|---|---|---|---|---|",
    ]
    for id, s in specs.items():
        tuples = sorted({point(b["metrics"]) for b in s["baselines"]})
        extra = [g for g in prior if g["instance"] == id]
        guards = "; ".join(str(g["XOR"])+" (depth unknown)" for g in s["literature_claims"]) or "—"
        points = ", ".join(sorted({point(g["metrics"]) for g in extra})) or "—"
        lines.append(f'| [{s["title"]}](../portfolio/{id}.json) | {s["kind"]} / {s["inputs"]} | {", ".join(tuples)} | {guards} | {points} |')
        corpus.append(dict(instance=id, kind=s["kind"], specification="portfolio/"+id+".json",
                           frozen_published_witnesses=s["baselines"],
                           count_only_claims=s["literature_claims"], post_freeze_prior=extra,
                           completeness="not certified; candidate-specific novelty audit required"))
    lines.extend([
        "\nThe six multipliers have widths 4, 5, 6, 7, 7 and 8, with two distinct "
        "degree-7 moduli; GF256 uses the AES polynomial 0x11b. "
        "Polynomial coefficient order is least significant bit first. A free field "
        "isomorphism is not allowed. Full modulus and port details are in each JSON.\n",
        "The two design problems fix four 4-bit words and branch number 5, with "
        "involution required in one. Arbitrary binary 4×4 blocks are allowed; the "
        "search sampled only a GF16 subfamily. Different matrices at the same "
        "coordinates do not count as progress. The GH1 and other SBP matrices "
        "are compared on those same design properties, not forced to equal a fixed map.\n",
        "All source and witness paths, metrics, and unresolved claims are retained "
        "in [the machine-readable evidence table](../results/portfolio-frontier.json). "
        "Count minima across multiplier points must not be combined into a "
        "fictitious joint AND/XOR/depth optimum.\n",
    ])
    (ROOT/"docs/PORTFOLIO.md").write_text("\n".join(lines))
    (ROOT/"results/portfolio-frontier.json").write_text(json.dumps(corpus, indent=2)+"\n")
    rejected = sum(v for k, v in statuses.items() if k.startswith("rejected"))
    report = [
        "# Launch assessment — 2026-10-20\n",
        "**Recommendation: postpone the cryptography launch.** This pilot has "
        "not demonstrated a sustained stream of independently established new "
        "published-frontier results. The local software and experiment are "
        "complete; the scientific launch criterion is unmet.\n",
        "This is a preliminary calibration of small search algorithms, not an "
        "evaluation of actual donated LLM-agent sessions. It neither proves "
        "that cryptographic optimization is exhausted nor establishes a true "
        "zero discovery rate. Unresolved novelty remains unresolved.\n",
        "## Measured outcome\n",
        "| Quantity | Result |",
        "|---|---:|",
        "| Fixed useful instances | 32: 24 linear maps, 6 multipliers, 2 MDS-design problems |",
        "| Frozen published baseline certificates | 59 |",
        f'| Completed seeded algorithm trials | {summary["completed_trials"]}/160; no missing trials |',
        f'| Trials improving the imported corpus | {summary["internal_advance_trials"]}/160 (80%) |',
        f'| Chronologically unique corpus Pareto proposals | {len(proposals)} |',
        f'| Proposals matched or dominated by checked prior | {rejected} |',
        f'| Proposals with unresolved published-frontier novelty | {statuses["unresolved-published-pareto-frontier"]} |',
        f'| Confirmed published-frontier advances | {summary["confirmed_published_frontier_advances"]} |',
        "| Actual donated-agent sessions / external novelty reviewers | 0 / 0 |",
        f'| Search CPU / sum of per-trial wall time | {summary["search_cpu_seconds"]:.2f} s / {summary["search_wall_seconds"]:.2f} s |',
        f'| Primary checking of all 284 retained trial certificates | {summary["primary_check_seconds"]:.2f} s |',
        f'| Second-check process time, 70 proposals: median / max | {statistics.median(times):.3f} s / {max(times):.3f} s |',
        f'| Second checks: 70 proposals plus 32 baseline controls | {summary["second_checks"]} successful; {summary["second_check_total_seconds"]:.2f} s total |',
        "\nThe 0/160 rate is the rate of **confirmed** advances in this bounded "
        "experiment. It is not an estimate of true novelty among unresolved "
        "proposals. Functional verification succeeded for all proposals. The "
        "second checker was implemented separately but by the same local "
        "author; no external review is implied. Human literature-review time "
        "and donated-agent token/time costs were not measured. Additional "
        "post-freeze prior checks are recorded separately and excluded from "
        "these experimental checking-time totals.\n",
        "| Wave (32 trials each) | Internal-advance trials | New corpus proposals | Confirmed published advances |",
        "|---|---:|---:|---:|",
    ]
    for w in summary["waves"]:
        report.append(f'| {w["wave"]+1} | {w["internal_advance_trials"]} | {w["unique_corpus_proposals"]} | {w["confirmed_published_advances"]} |')
    report.extend([
        "\nThe five waves used independent OS-random seeds and fixed work budgets. "
        "They always began from the frozen published corpus, not newly found "
        "circuits. Chronological deduplication prevents repeated rediscoveries "
        "or new matrices at old coordinates from looking like sustained progress. "
        "No independence-based confidence interval is justified. Wall timings "
        "were affected by concurrent work on the machine.\n",
        "## What the literature reconciliation changed\n",
        "The imported corpus was sourced from publications, not deliberately "
        "weakened. Nevertheless, a published archive is not the current "
        "frontier. Current NIST AES MixColumns witnesses, Xu–Sun's circulant "
        "constructions, Jain's released polynomial multipliers, and count-only "
        "claims stronger than available witnesses were included before search. "
        "Post-search SBP imports removed more apparent wins.\n",
        "- Four small cipher-map depth improvements are already present in "
        "the released SBP results. Published shallow MDS designs also eliminate "
        "several design proposals. The exact rejected hashes and dominating "
        "witnesses are recorded in the novelty audit.\n",
        "- ARIA's apparent 387→386 XOR reduction loses to a 384-XOR, depth-5 "
        "construction obtained by copying a 48-gate bit-plane already in the "
        "published artifact. That is a baseline correction, not a credited discovery.\n",
        "- No trial reduced the best imported multiplier AND count or established "
        "a new published minimum-XOR record. The remaining proposals concern "
        "depth tradeoffs or incomplete prior comparisons.\n",
        "- Quantum CNOT depth, mixed-fan-in gate counts, hardware GE, and free "
        "basis changes are not silently compared against binary-XOR SLP metrics.\n",
        "See [LITERATURE.md](LITERATURE.md) for primary references, precise access "
        "and normalization gaps, and the "
        "[per-candidate adjudications](../results/novelty-audit.json).\n",
        "## A verified transformation\n",
        "The GF(2^5), modulus 0x25 trial in wave 4 preserves 20 ANDs, 24 XORs "
        "and 44 total gates while reducing depth from 6 to 5. The complete "
        "1024-input multiplication table passes both checkers. This demonstrates "
        "a real equivalent transformation; its published novelty is unresolved.\n",
        "```sh\npython3 -I tools/check_submission.py portfolio/gf5-25.json results/candidates/w3-gf5-25-0.json\n"
        "python3 -I tools/audit_submission.py portfolio/gf5-25.json results/candidates/w3-gf5-25-0.json\n```\n",
        "## Decision and next evidence\n",
        "The preregistered screen required at least five audited new published "
        "points on at least three instances, including two in the last two "
        "waves, with second checks under 60 seconds. Correctness cost passed "
        "comfortably; demonstrated novelty did not. The screen was an "
        "operational choice, not a statistical theorem or a promised donor rate.\n",
        "Keep intake paused. First close the candidate-specific literature gaps "
        "and obtain external review. If continuing internal research, test "
        "cancellation-aware linear synthesis, structural multiplier "
        "decompositions, or bounded exact replacement in a new frozen experiment. "
        "The present cancellation-free synthesis and small rewrite walks used "
        "only about three CPU minutes of search in total, so they cannot rule "
        "out stronger methods. Only after promising audited yield should a "
        "separately authorized study measure fixed-budget real agent sessions "
        "and actual review costs. AES S-box synthesis remains a stretch track.\n",
        "The [task catalogue](../discover/catalog.json) records that research "
        "backlog. No remote repository, publication, messages, hub registration "
        "or donor intake was created. The manifest deliberately has no "
        "invented maintainer and is not eligible for public registration.\n",
    ])
    (ROOT/"docs/LAUNCH-ASSESSMENT.md").write_text("\n".join(report))
    artifacts = ["results/plan.json", "results/summary.json", "results/novelty-audit.json",
                 "results/portfolio-frontier.json", "sources/manifest.json"]
    frontier = dict(schema="discover-frontier/v0",
                    statement="32 fixed instances; 160 seeded algorithm trials; zero confirmed published-frontier advances. Correctness is verified; 55 proposal novelty judgments remain unresolved.",
                    status="LOCAL evaluation complete; launch postponed; no donor intake",
                    evidence_level=["author-checked"], claim_kind=["exact", "measured"],
                    scope="Binary XOR/AND, paid NOT, constants; separate Pareto axes. No global optimality or true-zero-discovery claim.",
                    metric=dict(name="confirmed published-advance trials", value="0/160"),
                    artifacts=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest())
                               for p in artifacts],
                    reproduce="python3 tools/check_all.py",
                    reproduce_minutes=2, prerequisites=["Python 3.9+"],
                    review="docs/LAUNCH-ASSESSMENT.md",
                    updated_on="2026-10-20")
    (ROOT/"discover/frontier.json").write_text(json.dumps(frontier, indent=2)+"\n")


if __name__ == "__main__":
    main()
