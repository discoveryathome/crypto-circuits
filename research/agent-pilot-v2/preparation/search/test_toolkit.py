#!/usr/bin/env python3
"""Small correctness and deterministic-seed tests, separate from timed sessions."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import run_search


def main():
    binary=HERE/'test-bin'
    subprocess.run(['c++','-O3','-std=c++17',str(HERE/'test_core.cpp'),'-o',str(binary)],check=True)
    result=subprocess.run([str(binary)],check=True,text=True,capture_output=True,timeout=90)
    (HERE/'test-circuits.jsonl').write_text(result.stdout)
    reports=[]
    targets=[[31,47,55,59,61,62],[31,47,55,59,61,62,0x80000001,0x40000003,0x20000007]]
    for line,rows in zip(result.stdout.splitlines(),targets):
        record=json.loads(line);c=record['circuit'];n=c['inputs']
        spec={'kind':'linear','inputs':n,'outputs':len(rows),
              'matrix':[[t>>i&1 for i in range(n)] for t in rows]}
        primary=run_search.verify(c,spec);second=run_search.scalar_checker()(spec,c)
        values=[1<<i for i in range(n)];cancellations=0
        for op,a,b in c['gates']:
            if values[a]&values[b]:cancellations+=1
            values.append(values[a]^values[b])
        reports.append({'method':record['method'],'primary':primary,'second':second,'semantic_cancellation_gates':cancellations})
    assert any(r['semantic_cancellation_gates'] for r in reports)
    report={'status':'passed','tests':result.stderr.strip(),'source_sha256':hashlib.sha256((HERE/'search.cpp').read_bytes()).hexdigest(),'certificates':reports}
    run_search.atomic_json(HERE/'tests.json',report)
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
