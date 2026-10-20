#!/usr/bin/env python3
"""Conservative, reproducible post-search novelty adjudication.

Known prior can disqualify a claim. Failure to find prior never certifies novelty.
This separate report does not alter the frozen experimental comparator.
"""
import collections
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from linear_pilot.synthesis import AXES


def read(path):
    return json.loads((ROOT/path).read_text())


def main():
    sbp = read("results/audit-baselines/sbp-verification.json")
    guards = []
    for r in sbp["records"]:
        guards.append(dict(instance=r["instance"], metrics=r["primary"]["metrics"],
                           path=r["path"], source=r["source"],
                           status="published-witness-verified-by-two-implementations",
                           url="https://github.com/demirmehmet0/SBP/tree/"+sbp["commit"]))
    aria = read("results/audit-baselines/aria-verification.json")
    guards.append(dict(instance="aria", metrics=aria["primary"]["metrics"],
                       path="results/audit-baselines/aria-published-lane-replication.json",
                       source=aria["source"], status="direct-derived-prior",
                       url="https://github.com/usnistgov/Circuits/tree/8366158a4324ef902ce740f29ddc9f7ebb1018b2"))
    judgments = {}
    for p in read("results/proposals.json"):
        prior = [g for g in guards if g["instance"] == p["instance"] and
                 all(g["metrics"][k] <= p["metrics"][k] for k in AXES)]
        spec = read("portfolio/"+p["instance"]+".json")
        if prior:
            status = "rejected-derived-prior-dominates" if p["instance"] == "aria" else "rejected-published-prior-matches-or-dominates"
            reason = "A verified prior construction is no worse on every Pareto axis."
        else:
            status = "unresolved-published-pareto-frontier"
            reason = ("Correctness established; candidate-specific published size/depth coverage "
                      "is incomplete. Not accepted as new. A count-only claim cannot settle "
                      "a depth tradeoff; absence from this corpus is insufficient.")
        judgments[p["sha256"]] = dict(
            instance=p["instance"], status=status, reason=reason,
            compared_metrics=p["metrics"],
            dominating_or_equal_prior=prior,
            sources=[g["url"] for g in prior] or [
                "https://csrc.nist.gov/projects/circuit-complexity/list-of-circuits",
                "https://github.com/Swapnil-jain/gf2m-circuits" if spec["kind"] == "multiplier"
                else "https://doi.org/10.7717/peerj-cs.1820",
                "docs/LITERATURE.md"],
            count_only_blockers=spec["literature_claims"],
            external_review=False)
    (ROOT/"results/novelty-audit.json").write_text(json.dumps(judgments, indent=2)+"\n")
    (ROOT/"results/post-freeze-prior.json").write_text(json.dumps(guards, indent=2)+"\n")
    print(json.dumps(dict(collections.Counter(j["status"] for j in judgments.values())), indent=2))


if __name__ == "__main__":
    main()
