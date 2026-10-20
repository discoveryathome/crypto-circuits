#!/usr/bin/env python3
"""Freeze a separate plan, then issue immutable timed session starts."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
IDS = ("square-aes-mugi", "whirlwindm0", "whirlwindm1")
NAMES = ("aes", "m0", "m1")
AXES = ("AND", "XOR", "total", "depth")


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+"\n")


def frontier(rows):
    # Keep one witness per nondominated coordinate, with published copies first.
    kept = []
    for r in sorted(rows, key=lambda x: x.get("kind") != "published"):
        m = r["metrics"]
        if any(all(k["metrics"][a] <= m[a] for a in AXES) for k in kept):
            continue
        kept = [k for k in kept if not all(m[a] <= k["metrics"][a] for a in AXES)]
        kept.append(r)
    return kept


def freeze():
    target = EXPERIMENT/"plan.json"
    if target.exists():
        raise SystemExit("plan already frozen")
    comparators = read(EXPERIMENT/"preparation/literature/comparators.json")
    rows = []
    for instance in IDS:
        for r in comparators["instances"][instance]["comparators"]:
            assert digest(ROOT/r["path"]) == r["sha256"]
            rows.append(dict(instance=instance, **r))
    write(EXPERIMENT/"initial-prior.json", rows)
    source_paths = [p for directory in ("preparation", "tools")
                    for p in (EXPERIMENT/directory).rglob("*")
                    if p.is_file() and p.suffix in (".py", ".cpp", ".md", ".json")
                    and "__pycache__" not in str(p) and "smoke-" not in str(p)]
    source_paths += [EXPERIMENT/"initial-prior.json", EXPERIMENT/"README.md"]
    checkers = [ROOT/"linear_pilot/checker.py", ROOT/"tools/check_submission.py",
                ROOT/"tools/audit_submission.py"]
    plan = dict(
        version=2, frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        purpose="Private screening of actual agent sessions; no donor launch authorization",
        instances=list(IDS), session_budget_seconds=1200,
        aggregate_session_cap_seconds=7200, concurrency=3,
        sessions=[dict(id=f"w{w}-{name}", wave=w, instance=id, seed=secrets.token_hex(16))
                  for w in (1, 2) for name, id in zip(NAMES, IDS)],
        specification_hashes={id: digest(ROOT/"portfolio"/(id+".json")) for id in IDS},
        trusted_checker_hashes={str(p.relative_to(ROOT)): digest(p) for p in checkers},
        initial_files={str(p.relative_to(ROOT)): digest(p) for p in source_paths},
        candidate_axes=list(AXES),
        seed_derivation="Full 128-bit hex session seed; default engine uses its low 64 bits. Further experiment seeds derive deterministically and are recorded.",
        stopping="1200 seconds from issued start; search processes use budget_run.py; up to two seconds cleanup grace; early stops retained.",
        wave2="All verified wave-1 candidates become known prior and available starts. Only independently adjudicated novel points count as discoveries.",
        novelty="Exact function and cost by both checkers; new nondominated cost tuple against published AND prior local work; candidate-specific independent-agent literature adjudication; unresolved comparators give zero credit.",
        decision=dict(min_confirmed_advances=2, min_distinct_instances=2,
                      min_wave2_advances=1, success="larger private beta only",
                      one_advance="investigate further; launch remains paused",
                      zero_advances="keep launch postponed"),
        costs="Actual session elapsed, child process CPU/wall, checker time, and reviewer elapsed recorded separately. Preparation start and model-token usage may be unavailable; never impute them.",
        limitations=["Small correlated sample; no IID confidence claim",
                     "Same default model family; fresh contexts and search seeds do not imply independent model sampling",
                     "Independent agents and code implementations are not external scientific reviewers"])
    write(target, plan)
    print(json.dumps(dict(path=str(target.relative_to(ROOT)), sha256=digest(target))))


def start(name):
    plan = read(EXPERIMENT/"plan.json")
    item = next(s for s in plan["sessions"] if s["id"] == name)
    directory = EXPERIMENT/"sessions"/name
    if (directory/"start.json").exists():
        raise SystemExit("session already started")
    for path, h in plan["initial_files"].items():
        if digest(ROOT/path) != h:
            raise SystemExit("frozen preparation changed: "+path)
    rows = [r for r in read(EXPERIMENT/"initial-prior.json") if r["instance"] == item["instance"]]
    if item["wave"] == 2:
        checks = read(EXPERIMENT/"review/checks.json")
        for r in checks.values():
            if r["wave"] == 1 and r["instance"] == item["instance"] and r["valid"]:
                rows.append(dict(instance=item["instance"], path=r["path"], sha256=r["sha256"],
                                 metrics=r["metrics"], kind="verified-wave1-local-prior",
                                 source="review/checks.json"))
    for r in rows:
        if digest(ROOT/r["path"]) != r["sha256"]:
            raise SystemExit("starting witness changed")
    write(directory/"starting-frontier.json", frontier(rows))
    write(directory/"all-known-prior.json", rows)
    now = datetime.datetime.now(datetime.timezone.utc)
    receipt = dict(**item, issued_at=now.isoformat(),
                   deadline=(now+datetime.timedelta(seconds=plan["session_budget_seconds"])).isoformat(),
                   plan_sha256=digest(EXPERIMENT/"plan.json"),
                   frontier_sha256=digest(directory/"starting-frontier.json"),
                   agent_task="session_"+name.replace("-", "_"),
                   model="inherited default; exact model/token accounting not exposed",
                   status="issued")
    (directory/"submissions").mkdir(exist_ok=True)
    write(directory/"start.json", receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("freeze")
    p = sub.add_parser("start")
    p.add_argument("session")
    args = parser.parse_args()
    freeze() if args.action == "freeze" else start(args.session)
