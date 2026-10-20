#!/usr/bin/env python3
"""Conservative novelty accounting; correctness is never treated as novelty."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from linear_pilot.synthesis import AXES, dominates


def read(path):
    return json.loads((ROOT/path).read_text())


def equal(a,b):
    return all(a[k] == b[k] for k in AXES)


def advance(metric, known):
    return not any(equal(metric,k) or dominates(k,metric) for k in known)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit",action="store_true",help="run second checker on all unique proposals and one baseline per instance")
    args = parser.parse_args()
    plan = read("results/plan.json")
    plan_hash = hashlib.sha256((ROOT/"results/plan.json").read_bytes()).hexdigest()
    specs = {e["id"]:read("portfolio/"+e["id"]+".json") for e in plan["instances"]}
    dynamic = {k:[b["metrics"] for b in s["baselines"]] for k,s in specs.items()}
    known_hashes = {hashlib.sha256((ROOT/b["path"]).read_bytes()).hexdigest()
                    for s in specs.values() for b in s["baselines"]}
    rows, proposals, missing = [], [], []
    for run in plan["runs"]:
        id, wave = run["instance"],run["wave"]
        path = ROOT/f"results/runs/w{wave}-{id}.json"
        if not path.exists():
            missing.append(run)
            continue
        r = json.loads(path.read_text())
        if r["plan_sha256"] != plan_hash or r["seed"] != run["seed"] or r["status"] != "complete":
            raise ValueError("receipt mismatch")
        spec = specs[id]
        internal = []
        unique = []
        for c in r["candidates"]:
            p = ROOT/c["path"]
            if hashlib.sha256(p.read_bytes()).hexdigest() != c["sha256"]:
                raise ValueError("candidate hash changed")
            metric = c["metrics"]
            baseline_metrics = [b["metrics"] for b in spec["baselines"]]
            if advance(metric,baseline_metrics):
                internal.append(c["path"])
            if advance(metric,dynamic[id]):
                dynamic[id] = [m for m in dynamic[id] if not dominates(metric,m)] + [metric]
                # Different matrices / programs at identical coordinates never
                # create repeat progress. Hash also filters exact rediscoveries.
                if c["sha256"] not in known_hashes:
                    pending = dict(instance=id,wave=wave,**c)
                    pending["beats_best_published_xor_count"] = metric["XOR"] < spec["best_published_xor_upper_bound"]
                    pending["literature_blockers"] = spec["literature_claims"]
                    pending["status"] = "corpus-frontier proposal; novelty unestablished"
                    proposals.append(pending)
                    unique.append(c["path"])
            known_hashes.add(c["sha256"])
        rows.append(dict(instance=id,wave=wave,internal_advance=bool(internal),
                         unique_corpus_proposals=unique,search_cpu_seconds=r["search_cpu_seconds"],
                         search_wall_seconds=r["search_wall_seconds"],
                         primary_check_seconds=sum(c["verification_seconds"] for c in r["candidates"])))
    audit_path = ROOT/"results/second-checks.json"
    audits = json.loads(audit_path.read_text()) if audit_path.exists() else {}
    if args.audit:
        targets = [(id,s["baselines"][0]["path"]) for id,s in specs.items()]
        targets += [(p["instance"],p["path"]) for p in proposals]
        for id,path in targets:
            h = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
            key = id+":"+h
            if key in audits:
                continue
            start = time.perf_counter()
            result = subprocess.run([sys.executable,"-I","tools/audit_submission.py",
                                     "portfolio/"+id+".json",path],cwd=ROOT,
                                    capture_output=True,text=True,timeout=120)
            if result.returncode:
                raise ValueError("Second checker failed: "+result.stdout+result.stderr)
            payload = json.loads(result.stdout)
            audits[key] = dict(instance=id,path=path,sha256=h,
                              process_wall_seconds=time.perf_counter()-start,**payload)
            audit_path.write_text(json.dumps(audits,indent=2)+"\n")
            print("second checker:",id,path,flush=True)
    adjudications = read("results/novelty-audit.json") if (ROOT/"results/novelty-audit.json").exists() else {}
    genuine = []
    for p in proposals:
        judgment = adjudications.get(p["sha256"],{})
        second = audits.get(p["instance"]+":"+p["sha256"],{})
        p["second_check_ok"] = second.get("ok",False)
        p["novelty_audit"] = judgment
        if judgment.get("status") == "published-frontier-advance" and judgment.get("sources") and second.get("ok"):
            genuine.append(p)
    rule = plan["decision_rule"]
    meets = (len(genuine) >= rule["min_unique_audited_published_advances"]
             and len({p["instance"] for p in genuine}) >= rule["min_distinct_instances"]
             and sum(p["wave"] >= 3 for p in genuine) >= rule["min_advances_in_last_two_waves"]
             and all(audits[p["instance"]+":"+p["sha256"]]["process_wall_seconds"] <= rule["max_second_check_seconds"]
                     for p in genuine) and not missing)
    summary = dict(
        planned_trials=len(plan["runs"]),completed_trials=len(rows),missing_trials=len(missing),
        internal_advance_trials=sum(r["internal_advance"] for r in rows),
        unique_corpus_frontier_proposals=len(proposals),
        confirmed_published_frontier_advances=len(genuine),
        confirmed_published_advance_trials=len({(p["wave"],p["instance"]) for p in genuine}),
        confirmed_rate_per_trial=len({(p["wave"],p["instance"]) for p in genuine})/len(rows) if rows else None,
        search_cpu_seconds=sum(r["search_cpu_seconds"] for r in rows),
        search_wall_seconds=sum(r["search_wall_seconds"] for r in rows),
        primary_check_seconds=sum(r["primary_check_seconds"] for r in rows),
        second_check_total_seconds=sum(v["process_wall_seconds"] for v in audits.values()),
        second_check_median_seconds=statistics.median(v["process_wall_seconds"] for v in audits.values()) if audits else None,
        second_check_max_seconds=max((v["process_wall_seconds"] for v in audits.values()),default=None),
        second_checks=len(audits),
        threshold_met=meets,
        recommendation="EXTERNAL REVIEW AND REAL AGENT TRIALS REQUIRED" if meets else "POSTPONE CRYPTOGRAPHY LAUNCH",
        limitation="Algorithm trials, not actual donated agents; short bounded methods do not establish exhaustion.",
        waves=[{"wave":w,"trials":sum(r["wave"]==w for r in rows),
                "internal_advance_trials":sum(r["wave"]==w and r["internal_advance"] for r in rows),
                "unique_corpus_proposals":sum(p["wave"]==w for p in proposals),
                "confirmed_published_advances":sum(p["wave"]==w for p in genuine)} for w in range(5)])
    (ROOT/"results/summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    (ROOT/"results/proposals.json").write_text(json.dumps(proposals,indent=2)+"\n")
    (ROOT/"results/trial-summary.json").write_text(json.dumps(rows,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
