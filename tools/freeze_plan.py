#!/usr/bin/env python3
"""Freeze literature guards, source hashes, seeds and decision rule BEFORE trials."""
import datetime
import hashlib
import json
from pathlib import Path
import secrets
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from linear_pilot.synthesis import dominates


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    plan_path = ROOT/"results/plan.json"
    if plan_path.exists():
        raise SystemExit("Plan exists: refusing to replace preregistration")
    ids = json.loads((ROOT/"portfolio/index.json").read_text())["instances"]
    # Explicit count-only guards: an unavailable depth never becomes an
    # invented full Pareto point. Sources retain their native gate models.
    guards = {
        "joltik":(43,"Yuan et al. 2024 table 2, citing Lin et al. 2021"),
        "smallscaleaes":(42,"Yuan et al. 2024 table 2, s-XOR embeds into general XOR"),
        "twofish":(110,"Yuan et al. 2024 table 2, s-XOR embeds into general XOR"),
        "anubis-clefiam0":(96,"Yuan et al. 2024 table 2 / Xu--Sun 2026 table 4"),
        "ls16-4x4-gf16":(43,"Yuan et al. 2024 table 2, citing Tan--Peyrin 2020 and Lin et al. 2021"),
        "bkl16-4x4-gf16":(40,"Yuan et al. 2024 table 2 CTG16 row; same authors as BKL16; identity must be checked"),
    }
    records = []
    for id in ids:
        path = ROOT/"portfolio"/(id+".json")
        s = json.loads(path.read_text())
        published = s["baselines"]
        best = min(x["metrics"]["XOR"] for x in published)
        extra = []
        if id in guards:
            g, source = guards[id]
            extra.append({"XOR":g,"depth":None,"source":source,
                          "status":"published-count-only; witness/port mapping unresolved"})
        s["literature_claims"] = extra
        s["best_published_xor_upper_bound"] = min([best]+[e["XOR"] for e in extra])
        s["novelty_policy"] = "Corpus advances are proposals. Published novelty needs candidate-specific literature audit and second checker."
        if id == "skinny":
            s["settled_count_control"] = "12 distinct non-input output forms require at least 12 gates; 12-XOR witness attains it."
        path.write_text(json.dumps(s,indent=2)+"\n")
        front = [x for x in published if not any(dominates(y["metrics"],x["metrics"]) for y in published)]
        records.append({"id":id,"kind":s["kind"],"spec_sha256":digest(path),
                        "baseline_frontier":[x["path"] for x in front]})
    seeds = [{"wave":wave,"instance":id,"seed":secrets.token_hex(16)}
             for wave in range(5) for id in ids]
    plan = {
        "version":1,"created_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "purpose":"Launch calibration, not a global optimality claim",
        "instances":records,"runs":seeds,
        "budgets":{"linear":{"paar_restarts":32,"walk_steps":256},
                   "multiplier":{"walk_steps":256},
                   "design":{"matrix_draws":256,"walk_steps":256}},
        "selection":"Frozen published-frontier starts, round-robin by wave; no feeding discoveries into later searches",
        "execution":"Sequential single-process seeded algorithm trials; not donated LLM-agent sessions",
        "decision_rule":{"min_unique_audited_published_advances":5,"min_distinct_instances":3,
                         "min_advances_in_last_two_waves":2,"max_second_check_seconds":60,
                         "requires_external_review_before_launch":True,
                         "if_unmet":"POSTPONE cryptography launch; no substitute internal leaderboard wins"},
        "statistics":"Describe exact sample. No iid binomial CI: shared methods/instances create dependence.",
        "files":{}
    }
    for folder in ("linear_pilot","tools","tests","portfolio","certificates"):
        for path in sorted((ROOT/folder).rglob("*")):
            if path.is_file() and "__pycache__" not in str(path):
                plan["files"][str(path.relative_to(ROOT))] = digest(path)
    plan_path.write_text(json.dumps(plan,indent=2)+"\n")
    print("Frozen",len(ids),"instances,",len(seeds),"trials",digest(plan_path))


if __name__ == "__main__":
    main()
