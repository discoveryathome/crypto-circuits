#!/usr/bin/env python3
"""Apply frozen screening rules to independent reviewer verdicts."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXP = Path(__file__).resolve().parents[1]
AXES = ("AND", "XOR", "total", "depth")


def read(path):
    return json.loads(path.read_text())


def point(record):
    return tuple(record["metrics"][a] for a in AXES)


def no_worse(a, b):
    return all(x <= y for x, y in zip(point(a), point(b)))


def frontier(rows):
    unique = {}
    for row in rows:
        unique.setdefault(point(row), row)
    return [r for p, r in sorted(unique.items())
            if not any(q != p and no_worse(s, r) for q, s in unique.items())]


def main():
    plan = read(EXP / "plan.json")
    digest = hashlib.sha256((EXP / "plan.json").read_bytes()).hexdigest()
    ledger = read(EXP / "review/checks.json")
    observed = read(EXP / "review/observed-summary.json")
    if any(s.get("summary") is None for s in observed["sessions"]):
        raise SystemExit("All issued sessions need final summaries")
    packets = []
    for wave in (1, 2):
        path = EXP / f"review/wave{wave}-adjudication.json"
        if not path.exists():
            raise SystemExit(f"Missing independent wave{wave} review")
        packet = read(path)
        if packet["plan_sha256"] != digest:
            raise SystemExit(f"Reviewer used different plan: wave{wave}")
        packets.append(packet)
    expected = {(s["session"], r["sha256"]) for s in observed["sessions"]
                for r in s["session_end_frontier_candidates"]}
    reviewed = {(r["session"], r["sha256"]) for p in packets for r in p["points"]}
    if expected != reviewed:
        raise SystemExit("Review packets must cover every final session frontier candidate")
    accepted, unresolved, rejected = [], [], []
    for packet in packets:
        for row in packet["points"]:
            key = row["session"] + ":" + row["sha256"]
            recorded = ledger[key]
            if not recorded["valid"] or point(row) != point(recorded):
                raise SystemExit(f"Unverified or inconsistent reviewed point: {key}")
            if hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() != row["sha256"]:
                raise SystemExit(f"Reviewed certificate changed: {key}")
            prior = read(EXP / "sessions" / row["session"] / "starting-frontier.json")
            if row["verdict"] == "accepted" and any(no_worse(p, row) for p in prior):
                raise SystemExit(f"Accepted point fails prior-frontier rule: {key}")
            target = {"accepted": accepted, "unresolved": unresolved,
                      "rejected": rejected}.get(row["verdict"])
            if target is None:
                raise SystemExit(f"Unrecognized review verdict: {row['verdict']}")
            target.append(row)
    coordinates = [(r["instance"], point(r)) for r in accepted]
    if len(set(coordinates)) != len(coordinates):
        raise SystemExit("Duplicate accepted coordinate across waves")
    instances = {r["instance"] for r in accepted}
    successful = {r["session"] for r in accepted}
    later = [r for r in accepted if r["wave"] == 2]
    rule = plan["decision"]
    passed = (len(accepted) >= rule["min_confirmed_advances"]
              and len(instances) >= rule["min_distinct_instances"]
              and len(later) >= rule["min_wave2_advances"])
    sessions = []
    for session in observed["sessions"]:
        name = session["session"]
        own = [r for r in accepted if r["session"] == name]
        first_submission = min((r["mtime_utc"] for r in own), default=None)
        adjudicated_at = next((p["review_ended_at"] for p in packets
                              if any(r["session"] == name and r["verdict"] == "accepted"
                                     for r in p["points"])), None)
        latency = None
        if first_submission:
            latency = (datetime.datetime.fromisoformat(first_submission) -
                       datetime.datetime.fromisoformat(session["issued_at"])).total_seconds()
        sessions.append({
            "session": name, "wave": session["wave"], "instance": session["instance"],
            "submitted_certificates": session["submissions"], "valid": session["valid"],
            "accepted_wave_end_points": len(own),
            "first_provisional_submission_seconds": session["first_eligible_submission_seconds"],
            "first_credited_wave_end_witness_submission_seconds": latency,
            "adjudicated_at": adjudicated_at,
            "accepted": [{k: r[k] for k in ("path", "sha256", "metrics", "claim_scope")}
                         for r in own],
        })
    retained = [r for r in accepted if not any(
        s["instance"] == r["instance"] and point(s) != point(r) and no_worse(s, r)
        for s in accepted)]
    result = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "plan_sha256": digest, "threshold_met": passed,
        "recommendation": "larger private beta only" if passed else
                          "investigate further; launch remains paused" if accepted else
                          "keep launch postponed",
        "confirmed_scope": "Independent-agent acceptance against reconciled identified literature; external review outstanding",
        "completed_sessions": len(sessions),
        "sessions_with_accepted_advances": len(successful),
        "successful_session_ids": sorted(successful),
        "instances_with_accepted_advances": sorted(instances),
        "accepted_wave_end_points": len(accepted),
        "accepted_wave2_points": len(later),
        "retained_accepted_frontier_points": len(retained),
        "unresolved_wave_end_points": len(unresolved),
        "rejected_wave_end_points": len(rejected),
        "submitted_certificates": observed["submitted_certificates"],
        "valid_certificates": observed["valid_certificates"],
        "invalid_certificates": observed["invalid_certificates"],
        "root_check_process_seconds": observed["root_check_process_seconds"],
        "root_check_median_seconds": observed["root_check_median_seconds"],
        "root_check_max_seconds": observed["root_check_max_seconds"],
        "independent_review_elapsed_seconds": sum(p["review_elapsed_seconds"] for p in packets),
        "sessions": sessions,
        "retained_accepted_frontier": [{k: r[k] for k in
            ("session", "wave", "instance", "path", "sha256", "metrics", "claim_scope")}
            for r in retained],
        "cost_limits": [
            "Model/token costs unavailable",
            "Preparation and root coordination active time not separately instrumented",
            "Some forced-stop process CPU accounting incomplete; do not treat raw receipt sum as total CPU",
        ],
        "inference_limits": [
            "Six correlated sessions on three selected maps; no IID population success estimate",
            "M0 and M1 are related Whirlwind maps",
            "Multiple Pareto points from one session are related constructions",
            "Passing this screen does not authorize launch or establish sustained long-term yield",
        ],
    }
    prior = read(EXP / "initial-prior.json")
    comparators = read(EXP / "preparation/literature/comparators.json")["instances"]
    verdicts = {(r["session"], r["sha256"]): r["verdict"]
                for p in packets for r in p["points"]}
    current = {}
    for instance in plan["instances"]:
        initial = [r for r in prior if r["instance"] == instance]
        new = [dict(r, kind="verified-local-agent-result",
                    adjudication=verdicts.get((r["session"], r["sha256"]),
                                             "superseded-checkpoint"))
               for r in ledger.values() if r["instance"] == instance and r["valid"]]
        def compact(rows):
            return [{k: r[k] for k in
                     ("path", "sha256", "kind", "source_url", "metrics",
                      "session", "wave", "adjudication") if k in r}
                    for r in rows]
        current[instance] = {
            "specification_sha256": plan["specification_hashes"][instance],
            "retrieved_published_frontier": compact(frontier(
                [r for r in initial if r["kind"] == "published"])),
            "current_verified_known_frontier": compact(frontier(initial + new)),
            "count_only_literature_guards": comparators[instance]["count_only_guards"],
        }
    (EXP / "review/current-frontier.json").write_text(json.dumps({
        "scope": "Selected fixed maps; correct local frontier is distinct from accepted novelty",
        "instances": current
    }, indent=2) + "\n")
    (EXP / "review/assessment.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ("sessions", "retained_accepted_frontier")}, indent=2))


if __name__ == "__main__":
    main()
