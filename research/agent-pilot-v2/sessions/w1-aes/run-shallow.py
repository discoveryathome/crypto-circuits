#!/usr/bin/env python3
"""Offline wrapper for original C++ search; each checkpoint passes two checkers."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from linear_pilot.checker import read_json, verify


def scalar_checker():
    spec = importlib.util.spec_from_file_location('independent_scalar_checker', ROOT/'tools/audit_submission.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.audit


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value, indent=2)+'\n')
    os.replace(temporary, path)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec', type=Path, required=True)
    p.add_argument('--start', type=Path, action='append', default=[])
    p.add_argument('--seed', type=int, required=True, help='unsigned 64-bit search seed')
    p.add_argument('--cpu-seconds', type=float, required=True)
    p.add_argument('--wall-seconds', type=float, default=None)
    p.add_argument('--output', type=Path, required=True)
    a=p.parse_args()
    if not 0<=a.seed<2**64: p.error('seed must be unsigned 64 bit')
    if a.cpu_seconds<=0: p.error('CPU budget must be positive')
    spec=read_json(a.spec)
    if spec['kind']!='linear' or spec['inputs']>63: p.error('fixed linear map with at most 63 inputs required')
    starts=a.start or [ROOT/x['path'] for x in spec['baselines']]
    output=a.output.resolve()
    if output.exists() and any(output.iterdir()): p.error('output directory must be empty/new')
    output.mkdir(parents=True, exist_ok=True)
    audit=scalar_checker()
    flat=[]
    for i,path in enumerate(starts):
        c=read_json(path); verify(c,spec); audit(spec,c)
        if any(g[0]!='XOR' or any(type(x) is not int for x in g[1:]) for g in c['gates']):
            p.error('search start requires XOR-only integer-wire circuit')
        if any(type(x) is not int for x in c['outputs']): p.error('constant outputs unsupported')
        target=output/f'start-{i}.txt'
        lines=[f"{c['inputs']} {len(c['gates'])} {len(c['outputs'])}"]
        lines.extend(f'{g[1]} {g[2]}' for g in c['gates'])
        lines.append(' '.join(map(str,c['outputs'])))
        target.write_text('\n'.join(lines)+'\n');flat.append(str(target))
    matrix=output/'matrix.txt'
    rows=[sum(int(x)<<i for i,x in enumerate(row)) for row in spec['matrix']]
    matrix.write_text(f"{spec['inputs']} {spec['outputs']}\n"+' '.join(map(str,rows))+'\n')
    binary=HERE/'shallow-bin'
    if not binary.exists() or binary.stat().st_mtime_ns < (HERE/'shallow.cpp').stat().st_mtime_ns:
        subprocess.run(['c++','-O3','-std=c++17',str(HERE/'shallow.cpp'),'-o',str(binary)],check=True)
    wall=a.wall_seconds or max(a.cpu_seconds*2,a.cpu_seconds+30)
    command=[str(binary),str(a.seed),str(a.cpu_seconds),str(wall),str(matrix),*flat]
    receipt={'spec':str(a.spec.resolve()),'spec_sha256':hashlib.sha256(a.spec.read_bytes()).hexdigest(),
             'source_sha256':hashlib.sha256((HERE/'shallow.cpp').read_bytes()).hexdigest(),
             'wrapper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
             'seed':a.seed,'cpu_seconds_budget':a.cpu_seconds,'wall_seconds_guard':wall,
             'starts':[{'path':str(s.resolve()),'sha256':hashlib.sha256(s.read_bytes()).hexdigest()} for s in starts],
             'checkpoints':[],'status':'running','method':'depth-3 all-support rank-DAG annealing with local coordinate partition minimization',
             'limitations':'Search is heuristic; exact distances do not prove globally optimal circuits. Wall/CPU stopping may change final iteration count.'}
    atomic_json(output/'receipt.json',receipt)
    begun=time.monotonic()
    with (output/'progress.log').open('w') as log, (output/'raw-checkpoints.jsonl').open('w') as raw:
        process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=log,text=True)
        try:
            for line in process.stdout:
                raw.write(line);raw.flush()
                record=json.loads(line);c=record.pop('circuit')
                primary=verify(c,spec);second=audit(spec,c)
                data=(json.dumps(c,sort_keys=True,separators=(',',':'))+'\n').encode()
                digest=hashlib.sha256(data).hexdigest();path=output/f'candidate-{digest}.json'
                path.write_bytes(data)
                record.update(path=str(path),sha256=digest,primary=primary,second=second)
                receipt['checkpoints'].append(record)
                atomic_json(output/'receipt.json',receipt)
                print(json.dumps({k:record[k] for k in ('method','iteration','cpu_seconds','XOR','depth','sha256')}),flush=True)
            code=process.wait(timeout=10)
            receipt.update(status='complete' if code==0 else 'failed',returncode=code,wall_seconds=time.monotonic()-begun)
            atomic_json(output/'receipt.json',receipt)
            if code: raise SystemExit(code)
        except BaseException:
            if process.poll() is None: process.terminate();process.wait(timeout=10)
            receipt.update(status='interrupted',wall_seconds=time.monotonic()-begun)
            atomic_json(output/'receipt.json',receipt)
            raise

if __name__=='__main__': main()
