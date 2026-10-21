"""Show verified known linear-map targets and unresolved literature guards."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from linear_pilot.checker import read_json, verify


def context(instance):
    plan = read_json(ROOT / "results/plan.json")
    spec_path = "portfolio/" + instance + ".json"
    if spec_path not in plan["files"]:
        raise ValueError("unknown pinned specification")
    if hashlib.sha256((ROOT / spec_path).read_bytes()).hexdigest() != plan["files"][spec_path]:
        raise ValueError("specification hash mismatch")
    spec = read_json(ROOT / spec_path)
    if spec["kind"] != "linear":
        raise ValueError("this task context is for fixed linear maps only")
    records = list(spec["baselines"])
    for path in sorted((ROOT / "results/runs").glob("w*-" + instance + ".json")):
        records.extend(read_json(path)["candidates"])
    records.extend(r for r in read_json(ROOT / "results/post-freeze-prior.json") if r["instance"] == instance)
    pilot = read_json(ROOT / "research/agent-pilot-v2/review/current-frontier.json")["instances"]
    if instance in pilot:
        records.extend(pilot[instance]["current_verified_known_frontier"])
    known = {}
    for r in records:
        path = ROOT / r["path"]
        h = hashlib.sha256(path.read_bytes()).hexdigest()
        if "sha256" in r and h != r["sha256"]:
            raise ValueError("candidate hash mismatch")
        metrics = verify(read_json(path), spec)["metrics"]
        if metrics != r["metrics"]:
            raise ValueError("candidate metrics mismatch")
        known[h] = {"path": r["path"], "sha256": h, "metrics": metrics}
    axes = ("AND", "XOR", "total", "depth")
    def dominates(a, b):
        return all(a[k] <= b[k] for k in axes) and any(a[k] < b[k] for k in axes)
    frontier = [r for r in known.values() if not any(dominates(q["metrics"], r["metrics"]) for q in known.values())]
    # Equal coordinates are already known even when their circuit hashes differ.
    unique = {}
    for r in sorted(frontier, key=lambda x: x["path"]):
        unique.setdefault(tuple(r["metrics"][k] for k in axes), r)
    return {"instance": instance, "specification_sha256": plan["files"][spec_path],
            "known_frontier": list(unique.values()),
            "published_xor_guard": spec.get("best_published_xor_upper_bound"),
            "literature_claims": spec.get("literature_claims", []),
            "novelty_policy": spec.get("novelty_policy"),
            "status": "PASS: known working targets; current external novelty review still required",
            "review_sources": ["docs/LITERATURE.md", "results/novelty-audit.json", "research/agent-pilot-v2/review/current-frontier.json"]}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("instance")
    args = p.parse_args()
    print(json.dumps(context(args.instance), indent=2))
