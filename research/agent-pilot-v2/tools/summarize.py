#!/usr/bin/env python3
"""Summarize observed certificates without making novelty decisions."""
import datetime
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[3]
EXP = Path(__file__).resolve().parents[1]
AXES = ("AND", "XOR", "total", "depth")


def read(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def point(record):
    return tuple(record["metrics"][axis] for axis in AXES)


def dominates(a, b):
    return all(x <= y for x, y in zip(point(a), point(b)))


def frontier(records):
    """One earliest observed certificate per nondominated coordinate."""
    unique = {}
    for record in sorted(records, key=lambda r: r.get("mtime_utc", "")):
        unique.setdefault(point(record), record)
    return [r for p, r in sorted(unique.items())
            if not any(q != p and dominates(s, r)
                       for q, s in unique.items())]


def compact(record):
    return {k: record[k] for k in
            ("session", "wave", "instance", "path", "sha256", "metrics",
             "mtime_utc", "observed_at") if k in record}


def main():
    plan = read(EXP / "plan.json")
    records = list(read(EXP / "review/checks.json", {}).values())
    report = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scope": "Observed correctness and Pareto comparisons, not novelty",
        "sessions": [],
        "submitted_certificates": len(records),
        "valid_certificates": sum(r["valid"] for r in records),
        "invalid_certificates": sum(not r["valid"] for r in records),
        "root_check_process_seconds": sum(r["checking_seconds"] for r in records),
        "model_token_cost": None,
        "model_token_cost_reason": "Not exposed by orchestration interface",
    }
    check_times = [r["checking_seconds"] for r in records]
    report["root_check_median_seconds"] = statistics.median(check_times) if check_times else None
    report["root_check_max_seconds"] = max(check_times, default=None)
    for session in plan["sessions"]:
        name = session["id"]
        directory = EXP / "sessions" / name
        start = read(directory / "start.json")
        if start is None:
            report["sessions"].append(dict(session=name, status="not-issued"))
            continue
        prior = read(directory / "starting-frontier.json")
        own = [r for r in records if r["session"] == name]
        valid = [r for r in own if r["valid"]]
        eligible = [r for r in valid if not any(dominates(p, r) for p in prior)]
        times = [r["mtime_utc"] for r in eligible]
        first = min(times, default=None)
        latency = None
        if first is not None:
            latency = (datetime.datetime.fromisoformat(first) -
                       datetime.datetime.fromisoformat(start["issued_at"])).total_seconds()
        processes = []
        if (directory / "processes.jsonl").exists():
            processes = [json.loads(line) for line in
                         (directory / "processes.jsonl").read_text().splitlines()
                         if line.strip()]
        report["sessions"].append({
            "session": name, "instance": session["instance"], "wave": session["wave"],
            "issued_at": start["issued_at"], "deadline": start["deadline"],
            "summary": read(directory / "session-summary.json"),
            "submissions": len(own), "valid": len(valid),
            "unique_cost_points": len({point(r) for r in valid}),
            "points_advancing_starting_prior": len({point(r) for r in eligible}),
            "session_end_frontier_candidates": [compact(r) for r in frontier(eligible)],
            "first_eligible_submission_seconds": latency,
            "first_eligible_submission_at": first,
            "root_check_seconds": sum(r["checking_seconds"] for r in own),
            "process_records": processes,
        })
    report["combined_candidate_frontiers"] = {
        instance: [compact(r) for r in frontier(
            [r for r in records if r["valid"] and r["instance"] == instance])]
        for instance in plan["instances"]
    }
    path = EXP / "review/observed-summary.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items()
                      if k not in ("sessions", "combined_candidate_frontiers")}, indent=2))
    for session in report["sessions"]:
        print(session["session"], [
            (r["metrics"]["XOR"], r["metrics"]["depth"])
            for r in session.get("session_end_frontier_candidates", [])
        ])


if __name__ == "__main__":
    main()
