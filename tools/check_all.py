#!/usr/bin/env python3
"""Offline integrity and independent primary recheck of every shipped witness."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from linear_pilot.checker import read_json, verify


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baselines-only",action="store_true")
    args = parser.parse_args()
    began = time.perf_counter()
    plan = read_json(ROOT/"results/plan.json")
    for path, h in plan["files"].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != h:
            raise ValueError("frozen file changed: "+path)
    manifest = ROOT/"sources/manifest.json"
    if manifest.exists():
        for x in read_json(manifest)["files"]:
            if hashlib.sha256((ROOT/x["path"]).read_bytes()).hexdigest() != x["sha256"]:
                raise ValueError("source changed: "+x["path"])
    count = 0
    specs = {}
    for item in plan["instances"]:
        spec = read_json(ROOT/"portfolio"/(item["id"]+".json"))
        specs[item["id"]] = spec
        for b in spec["baselines"]:
            result = verify(read_json(ROOT/b["path"]),spec)
            if result["metrics"] != b["metrics"]:
                raise ValueError("baseline metrics changed")
            count += 1
    if not args.baselines_only:
        for run in plan["runs"]:
            r = read_json(ROOT/f'results/runs/w{run["wave"]}-{run["instance"]}.json')
            if r["seed"] != run["seed"]:
                raise ValueError("seed mismatch")
            for c in r["candidates"]:
                if hashlib.sha256((ROOT/c["path"]).read_bytes()).hexdigest() != c["sha256"]:
                    raise ValueError("candidate changed")
                result = verify(read_json(ROOT/c["path"]),specs[run["instance"]])
                if result["metrics"] != c["metrics"]:
                    raise ValueError("candidate metrics changed")
                count += 1
    # Post-freeze literature witnesses are separate from experimental inputs.
    guards = ROOT/"results/post-freeze-prior.json"
    if guards.exists():
        for g in read_json(guards):
            result = verify(read_json(ROOT/g["path"]), specs[g["instance"]])
            if result["metrics"] != g["metrics"]:
                raise ValueError("post-freeze prior metrics changed")
            count += 1
    # Check agreement of the separately implemented evaluator's archived metrics.
    audits = ROOT/"results/second-checks.json"
    if audits.exists():
        for a in read_json(audits).values():
            if hashlib.sha256((ROOT/a["path"]).read_bytes()).hexdigest() != a["sha256"]:
                raise ValueError("secondary certificate changed")
            result = verify(read_json(ROOT/a["path"]), specs[a["instance"]])
            if not a["ok"] or any(result["metrics"][k] != v for k, v in a["metrics"].items()):
                raise ValueError("checkers disagree")
    print(json.dumps({"ok":True,"certificates_checked":count,
                      "wall_seconds":time.perf_counter()-began}))


if __name__ == "__main__":
    main()
