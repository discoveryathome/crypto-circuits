#!/usr/bin/env python3
"""Import published SBP result data as post-freeze literature guards.

No upstream code is executed and no experimental input is changed.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from linear_pilot.checker import verify, Invalid


def parse(path):
    refs = {"x"+str(i): i for i in range(16)}
    outputs, gates = {}, []
    pattern = re.compile(r"(t\d+)\s*=\s*([xt]\d+)\s*\+\s*([xt]\d+)\s*(?:\*\s*(y\d+))?\s*\(\d+\)")
    for line in path.read_text().splitlines():
        if "=" not in line:
            continue
        alias = re.fullmatch(r"(y\d+)\s*=\s*(x\d+)\s*\*\s*\(0\)", line.strip())
        if alias:
            out, source = alias.groups()
            if out in outputs:
                raise ValueError("repeated output")
            outputs[out] = refs[source]
            continue
        match = pattern.fullmatch(line.strip())
        if match is None:
            raise ValueError("unexpected source assignment: "+line)
        target, a, b, out = match.groups()
        if target in refs:
            raise ValueError("repeated assignment")
        gates.append(["XOR", refs[a], refs[b]])
        refs[target] = 16+len(gates)-1
        if out:
            if out in outputs:
                raise ValueError("repeated output")
            outputs[out] = refs[target]
    return dict(inputs=16, gates=gates, outputs=[outputs["y"+str(i)] for i in range(16)])


def main():
    directory = ROOT/"results/audit-baselines"
    directory.mkdir(exist_ok=True)
    specs = [json.loads(p.read_text()) for p in (ROOT/"portfolio").glob("*.json")]
    specs = [s for s in specs if s.get("inputs") == 16 and s["kind"] != "multiplier"]
    records, unmatched = [], []
    cache_path = directory/"sbp-second-cache.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    for source in sorted((ROOT/"sources/sbp/SBP/result").rglob("*SBP*.txt")):
        c = parse(source)
        matches = []
        for spec in specs:
            try:
                primary = verify(c, spec)
            except Invalid:
                continue
            path = directory/(spec["id"]+"--sbp--"+source.stem+".json")
            path.write_text(json.dumps(c, indent=2)+"\n")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            key = spec["id"]+":"+digest
            if key not in cache:
                result = subprocess.run([sys.executable, "-I", "tools/audit_submission.py",
                                         "portfolio/"+spec["id"]+".json", str(path)],
                                        cwd=ROOT, capture_output=True, text=True, check=True)
                cache[key] = json.loads(result.stdout)
                cache_path.write_text(json.dumps(cache, indent=2)+"\n")
            second = cache[key]
            records.append(dict(instance=spec["id"], path=str(path.relative_to(ROOT)),
                                source=str(source.relative_to(ROOT)),
                                sha256=digest,
                                primary=primary, secondary=second,
                                classification="published prior; imported after frozen experiment"))
            matches.append(spec["id"])
        if not matches:
            unmatched.append(str(source.relative_to(ROOT)))
        print(source.name, matches, flush=True)
    report = dict(source="https://github.com/demirmehmet0/SBP",
                  commit=json.loads((ROOT/"sources/sbp-tree.json").read_text())["sha"],
                  records=records, unmatched=unmatched,
                  note="Unmatched files are not claimed to implement portfolio problems.")
    (directory/"sbp-verification.json").write_text(json.dumps(report, indent=2)+"\n")


if __name__ == "__main__":
    main()
