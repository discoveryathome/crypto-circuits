#!/usr/bin/env python3
"""Reproduce a stronger PRIOR-derived guard, not an experimental discovery."""
import json
from pathlib import Path
import sys
import subprocess
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from linear_pilot.synthesis import prune
from linear_pilot.checker import verify

spec = json.loads((ROOT/"portfolio/aria.json").read_text())
base = json.loads((ROOT/spec["baselines"][0]["path"]).read_text())
assert all(all(not b or j%8 == i%8 for j,b in enumerate(row)) for i,row in enumerate(spec["matrix"]))
lane = prune(dict(base,outputs=base["outputs"][::8]))
gates, outputs = [], [None]*128
for bit in range(8):
    refs = {i:8*(i//8)+bit for i in range(0,128,8)}
    for k,g in enumerate(lane["gates"]):
        gates.append([g[0],*(refs[x] for x in g[1:])])
        refs[128+k] = 128+len(gates)-1
    for word,out in enumerate(lane["outputs"]):
        outputs[8*word+bit] = refs[out]
c = dict(inputs=128,gates=gates,outputs=outputs)
directory = ROOT/"results/audit-baselines"
directory.mkdir(exist_ok=True)
path = directory/"aria-published-lane-replication.json"
path.write_text(json.dumps(c,indent=2)+"\n")
primary = verify(c,spec)
second = subprocess.run([sys.executable,"-I","tools/audit_submission.py","portfolio/aria.json",
                         str(path)],cwd=ROOT,capture_output=True,text=True,check=True)
report = {"primary":primary,"secondary":json.loads(second.stdout),
          "source":spec["baselines"][0]["origin"],
          "method":"Copy the published circuit's bit-0 cone eight times",
          "classification":"derived-prior baseline correction, not counted as a trial discovery"}
(directory/"aria-verification.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
