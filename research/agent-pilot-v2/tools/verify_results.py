#!/usr/bin/env python3
"""Fresh, data-only verification of the experiment's recorded submissions."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
EXP = Path(__file__).resolve().parents[1]
PLAN_SHA256 = "e13c95221645d66df1ba36c59df662d3dbb4e8b0ae82dcce8045911a339b0097"
AXES = ("AND", "XOR", "total", "depth")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_hash(path, expected):
    if digest(path) != expected:
        raise SystemExit(f"Hash mismatch: {path}")


def main():
    began = time.perf_counter()
    require_hash(EXP / "plan.json", PLAN_SHA256)
    plan = json.loads((EXP / "plan.json").read_text())
    pinned = dict(plan["initial_files"])
    pinned.update(plan["trusted_checker_hashes"])
    for instance, sha in plan["specification_hashes"].items():
        pinned[f"portfolio/{instance}.json"] = sha
    for record in json.loads((EXP / "initial-prior.json").read_text()):
        pinned[record["path"]] = record["sha256"]
    for path, sha in pinned.items():
        require_hash(ROOT / path, sha)
    ledger = json.loads((EXP / "review/checks.json").read_text())
    session_ids = {s["id"]: s["instance"] for s in plan["sessions"]}
    expected_keys = set()
    submission_files = 0
    for name in session_ids:
        directory = EXP / "sessions" / name
        if not directory.exists():
            continue
        start = json.loads((directory / "start.json").read_text())
        require_hash(directory / "starting-frontier.json", start["frontier_sha256"])
        if start["plan_sha256"] != PLAN_SHA256:
            raise SystemExit(f"Session plan mismatch: {name}")
        context_path = directory / "context-receipt.json"
        if context_path.exists():
            context = json.loads(context_path.read_text())
            require_hash(ROOT / context["handoff_path"], context["handoff_sha256"])
            require_hash(ROOT / context["review_path"], context["review_sha256"])
        for path in (directory / "submissions").glob("*.json"):
            expected_keys.add(name + ":" + digest(path))
            submission_files += 1
    if expected_keys != set(ledger):
        raise SystemExit("Submission inventory and ledger disagree; run collect.py first")
    checked = 0
    verification_times = []
    for key, record in ledger.items():
        if session_ids[record["session"]] != record["instance"]:
            raise SystemExit(f"Instance mismatch: {key}")
        candidate = ROOT / record["path"]
        require_hash(candidate, record["sha256"])
        if key != record["session"] + ":" + record["sha256"]:
            raise SystemExit(f"Ledger key mismatch: {key}")
        spec = ROOT / "portfolio" / (record["instance"] + ".json")
        for checker in ("check_submission.py", "audit_submission.py"):
            before = time.perf_counter()
            result = subprocess.run(
                [sys.executable, "-I", str(ROOT / "tools" / checker),
                 str(spec), str(candidate)], cwd=ROOT,
                capture_output=True, text=True, timeout=60)
            payload = json.loads(result.stdout)
            valid = result.returncode == 0 and payload.get("ok", False)
            if valid != record["valid"]:
                raise SystemExit(f"Correctness result changed: {key}, {checker}")
            if valid and any(payload["metrics"][axis] != record["metrics"][axis]
                             for axis in AXES):
                raise SystemExit(f"Metrics changed: {key}, {checker}")
            verification_times.append(time.perf_counter() - before)
            checked += 1
    print(json.dumps({
        "ok": True, "plan_sha256": PLAN_SHA256,
        "pinned_files": len(pinned), "certificates": len(ledger),
        "submission_files": submission_files,
        "fresh_checker_processes": checked,
        "checker_process_seconds": sum(verification_times),
        "total_wall_seconds": time.perf_counter() - began,
        "scope": "Integrity, exact function, and costs; novelty is separately reviewed"
    }, indent=2))


if __name__ == "__main__":
    main()
