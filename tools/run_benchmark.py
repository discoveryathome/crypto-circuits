#!/usr/bin/env python3
"""Run the frozen, independently seeded portfolio experiment.

Each trial writes an immutable receipt and certificates. It never edits the
published baselines or declares novelty. Interruption/resume keeps every seed
and denominator. No network or untrusted executable is involved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from linear_pilot.synthesis import metrics, dominates, paar, walk, AXES
from linear_pilot.design_search import sample
from linear_pilot.checker import verify


def read(path):
    return json.loads((ROOT/path).read_text())


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    p = ROOT/path
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2)+"\n")


def frontier(candidates):
    out = []
    for c in candidates:
        m = metrics(c)
        if any(all(metrics(x)[k] == m[k] for k in AXES) or dominates(metrics(x),m) for x in out):
            continue
        out = [x for x in out if not dominates(m,metrics(x))]
        out.append(c)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave",type=int,choices=range(5))
    parser.add_argument("--instance")
    args = parser.parse_args()
    plan = read("results/plan.json")
    for path, expected in plan["files"].items():
        if hash_file(ROOT/path) != expected:
            raise SystemExit("Frozen input changed: "+path)
    plan_hash = hash_file(ROOT/"results/plan.json")
    entries = {e["id"]:e for e in plan["instances"]}
    for run in plan["runs"]:
        if args.wave is not None and run["wave"] != args.wave:
            continue
        if args.instance is not None and run["instance"] != args.instance:
            continue
        instance, wave = run["instance"], run["wave"]
        dest = f"results/runs/w{wave}-{instance}.json"
        if (ROOT/dest).exists():
            receipt = read(dest)
            if receipt["plan_sha256"] != plan_hash or receipt["seed"] != run["seed"]:
                raise SystemExit("Mismatched existing receipt")
            continue
        spec = read("portfolio/"+instance+".json")
        starts = entries[instance]["baseline_frontier"]
        # Every trial starts from a frozen published circuit. Discoveries do not
        # contaminate later trials; analysis separately deduplicates their gains.
        start_path = starts[wave % len(starts)]
        start = read(start_path)
        rng = random.Random(int(run["seed"],16))
        began, cpu = time.perf_counter(), time.process_time()
        candidates = [start]
        budget = plan["budgets"][spec["kind"]]
        counters = {}
        if spec["kind"] == "linear":
            for i in range(budget["paar_restarts"]):
                candidates.append(paar(spec["matrix"],rng,bool(i%2)))
            counters["paar_restarts"] = budget["paar_restarts"]
        elif spec["kind"] == "design":
            generated,counters = sample(rng,budget["matrix_draws"],spec["involutory"])
            candidates.extend(generated)
        walked, changes = walk(start,rng,budget["walk_steps"],spec["kind"] == "multiplier")
        candidates.extend(walked)
        counters.update(walk_steps=budget["walk_steps"],accepted_walk_changes=changes,
                        candidates_considered=len(candidates))
        selected = frontier(candidates)
        search_wall, search_cpu = time.perf_counter()-began,time.process_time()-cpu
        verified = []
        for i,c in enumerate(selected):
            result = verify(c,spec)
            path = f"results/candidates/w{wave}-{instance}-{i}.json"
            save(path,c)
            verified.append(dict(path=path,sha256=hash_file(ROOT/path),**result))
        receipt = dict(instance=instance,wave=wave,seed=run["seed"],plan_sha256=plan_hash,
                       start=start_path,search_wall_seconds=search_wall,search_cpu_seconds=search_cpu,
                       counters=counters,candidates=verified,python=sys.version,
                       platform=platform.platform(),status="complete")
        save(dest,receipt)
        print(f"wave={wave} {instance}: {len(selected)} checked; search {search_cpu:.3f} CPU s / {search_wall:.3f} wall s",
              flush=True)


if __name__ == "__main__":
    main()
