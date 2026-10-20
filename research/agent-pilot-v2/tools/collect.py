#!/usr/bin/env python3
"""Trusted data-only checking and chronological submission ledger."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
AXES = ("AND", "XOR", "total", "depth")


def read(path):
    return json.loads(path.read_text())


def no_better(a, b):
    return all(a[k] <= b[k] for k in AXES)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session")
    args = parser.parse_args()
    plan = read(EXPERIMENT/"plan.json")
    for path, digest in plan["trusted_checker_hashes"].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != digest:
            raise SystemExit("trusted checker changed")
    ledger_path = EXPERIMENT/"review/checks.json"
    ledger = read(ledger_path) if ledger_path.exists() else {}
    for session in plan["sessions"]:
        name, instance = session["id"], session["instance"]
        if args.session and name != args.session:
            continue
        directory = EXPERIMENT/"sessions"/name
        if not (directory/"start.json").exists():
            continue
        start = read(directory/"start.json")
        guard = read(directory/"starting-frontier.json")
        if hashlib.sha256((directory/"starting-frontier.json").read_bytes()).hexdigest() != start["frontier_sha256"]:
            raise SystemExit("starting frontier changed")
        spec = ROOT/"portfolio"/(instance+".json")
        if hashlib.sha256(spec.read_bytes()).hexdigest() != plan["specification_hashes"][instance]:
            raise SystemExit("specification changed")
        for path in sorted((directory/"submissions").glob("*.json")):
            if path.stat().st_size > 2_000_000:
                raise SystemExit("oversized submission")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            key = name+":"+digest
            if key in ledger:
                continue
            began = time.perf_counter()
            checks = []
            for tool in ("check_submission.py", "audit_submission.py"):
                before = time.perf_counter()
                p = subprocess.run([sys.executable, "-I", str(ROOT/"tools"/tool),
                                    str(spec), str(path)], cwd=ROOT,
                                   capture_output=True, text=True, timeout=60)
                try:
                    payload = json.loads(p.stdout)
                except ValueError:
                    payload = dict(ok=False, error=p.stderr or p.stdout)
                checks.append(dict(tool=tool, returncode=p.returncode,
                                   process_wall_seconds=time.perf_counter()-before,
                                   result=payload))
            valid = all(c["returncode"] == 0 and c["result"].get("ok") for c in checks)
            m = checks[0]["result"].get("metrics")
            if valid:
                if any(m[k] != checks[1]["result"]["metrics"][k] for k in AXES):
                    raise SystemExit("independent checkers disagree")
            known = [g for g in guard if valid and no_better(g["metrics"], m)]
            duplicate = [k for k, r in ledger.items()
                         if r["instance"] == instance and r["valid"] and
                         all(r["metrics"][a] == m[a] for a in AXES)] if valid else []
            ledger[key] = dict(session=name, wave=session["wave"], instance=instance,
                               path=str(path.relative_to(ROOT)), sha256=digest,
                               observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                               mtime_utc=datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).isoformat(),
                               valid=valid, metrics=m, checks=checks,
                               checking_seconds=time.perf_counter()-began,
                               matched_or_dominated_starting_prior=[g["path"] for g in known],
                               duplicate_cost_points=duplicate,
                               status=("invalid" if not valid else "known-or-dominated" if known or duplicate
                                       else "candidate-needing-literature-adjudication"))
            ledger_path.parent.mkdir(exist_ok=True)
            ledger_path.write_text(json.dumps(ledger, indent=2)+"\n")
            print(name, m, ledger[key]["status"], flush=True)
    print(json.dumps(dict(submissions=len(ledger),
                          valid=sum(r["valid"] for r in ledger.values()),
                          candidates=sum(r["status"] == "candidate-needing-literature-adjudication"
                                         for r in ledger.values()))))


if __name__ == "__main__":
    main()
