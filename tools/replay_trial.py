#!/usr/bin/env python3
"""Replay one recorded trial in a fresh temporary checkout; compare certificates."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--instance",required=True)
    p.add_argument("--wave",type=int,default=0,choices=range(5))
    args = p.parse_args()
    plan = json.loads((ROOT/"results/plan.json").read_text())
    if args.instance not in {x["id"] for x in plan["instances"]}:
        raise SystemExit("unknown instance")
    (ROOT/"work").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT/"work",prefix="replay-") as temp:
        target = Path(temp)
        for path in list(plan["files"])+["results/plan.json"]:
            dst = target/path
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/path,dst)
        subprocess.run([sys.executable,"tools/run_benchmark.py","--instance",args.instance,
                        "--wave",str(args.wave)],cwd=target,check=True)
        receipt = f"results/runs/w{args.wave}-{args.instance}.json"
        a = json.loads((ROOT/receipt).read_text())
        b = json.loads((target/receipt).read_text())
        if [c["sha256"] for c in a["candidates"]] != [c["sha256"] for c in b["candidates"]]:
            raise SystemExit("replay differs")
        print(json.dumps({"ok":True,"instance":args.instance,"wave":args.wave,
                          "matching_certificates":len(a["candidates"]),
                          "timings_excluded_from_equality":True}))


if __name__ == "__main__":
    main()
