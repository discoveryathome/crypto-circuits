#!/usr/bin/env python3
"""Second implementation: scalar Boolean evaluation, no pilot-code imports.

Usage: python3 -I tools/audit_submission.py SPEC CANDIDATE
Linear proof: zero and basis vectors, AFTER rejecting every nonlinear gate.
Design proof: all 65,535 nonzero inputs, exact word branch number and M(Mx)=x.
Multipliers: all pairs, shift/reduce field arithmetic independent of primary
checker's polynomial convolution/long-division implementation.
"""
import json
from pathlib import Path
import sys
import time


def load(path):
    p = Path(path)
    if p.stat().st_size > 2_000_000:
        raise ValueError("size limit")
    def pairs(items):
        d = {}
        for k,v in items:
            if k in d:
                raise ValueError("duplicate key")
            d[k] = v
        return d
    return json.loads(p.read_text(), object_pairs_hook=pairs)


def audit(spec, c):
    started = time.perf_counter()
    n, m = spec["inputs"], spec["outputs"]
    if type(c) is not dict or set(c) != {"inputs","gates","outputs"}:
        raise ValueError("schema")
    if type(c["inputs"]) is not int or c["inputs"] != n:
        raise ValueError("input count")
    if type(c["gates"]) is not list or len(c["gates"]) > 10000:
        raise ValueError("gates")
    if type(c["outputs"]) is not list or len(c["outputs"]) != m:
        raise ValueError("outputs")
    depth = [0]*n
    counts = dict(AND=0,XOR=0,NOT=0)
    def valid(r, bound):
        return (type(r) is int and 0 <= r < bound) or (type(r) is str and r in ("0","1"))
    for i,g in enumerate(c["gates"]):
        if type(g) is not list or not g or type(g[0]) is not str or g[0] not in counts:
            raise ValueError("operation")
        if len(g) != (2 if g[0] == "NOT" else 3):
            raise ValueError("arity")
        if spec["kind"] != "multiplier" and g[0] == "AND":
            raise ValueError("nonlinear gate in affine proof")
        if not all(valid(r,n+i) for r in g[1:]):
            raise ValueError("invalid reference")
        depth.append(1+max(depth[r] if type(r) is int else 0 for r in g[1:]))
        counts[g[0]] += 1
    if not all(valid(r,len(depth)) for r in c["outputs"]):
        raise ValueError("output reference")
    def evaluate(word):
        v = [(word >> i) & 1 for i in range(n)]
        def value(r):
            return v[r] if type(r) is int else int(r)
        for g in c["gates"]:
            a = value(g[1])
            if g[0] == "NOT":
                v.append(1-a)
            elif g[0] == "XOR":
                v.append(a ^ value(g[2]))
            else:
                v.append(a & value(g[2]))
        return sum(value(r) << i for i,r in enumerate(c["outputs"]))
    checked = 0
    if spec["kind"] == "linear":
        if evaluate(0) != 0:
            raise ValueError("constant")
        for i in range(n):
            expected = sum(spec["matrix"][j][i] << j for j in range(m))
            if evaluate(1 << i) != expected:
                raise ValueError("wrong matrix")
        checked = n+1
    elif spec["kind"] == "multiplier":
        w, p = spec["width"], spec["modulus"]
        for a in range(1 << w):
            for b in range(1 << w):
                x,y,z = a,b,0
                while y:
                    if y & 1:
                        z ^= x
                    y >>= 1
                    x <<= 1
                    if x & (1 << w):
                        x ^= p
                if evaluate(a | b << w) != z:
                    raise ValueError("wrong field product")
                checked += 1
    elif spec["kind"] == "design":
        # Exhaustive scalar circuit results also establish the actual branch
        # number, independently of the primary checker's minor criterion.
        if evaluate(0) != 0:
            raise ValueError("nonlinear/affine design")
        minimum = 8
        outputs = [evaluate(x) for x in range(65536)]
        for x in range(1,65536):
            y = outputs[x]
            weight = sum(bool((x >> (4*i)) & 15)+bool((y >> (4*i)) & 15) for i in range(4))
            minimum = min(minimum,weight)
            if weight < 5:
                raise ValueError("branch number below 5")
            if spec["involutory"] and outputs[y] != x:
                raise ValueError("not involutory")
        if minimum != 5:
            raise ValueError("branch number")
        checked = 65536
    else:
        raise ValueError("unknown profile")
    return {"ok":True,"method":"independent scalar implementation","evaluations":checked,
            "metrics":dict(counts,total=len(c["gates"]),
                           depth=max(depth[r] if type(r) is int else 0 for r in c["outputs"])),
            "verification_seconds":time.perf_counter()-started}


if __name__ == "__main__":
    try:
        print(json.dumps(audit(load(sys.argv[1]),load(sys.argv[2])),sort_keys=True))
    except (ValueError,TypeError,KeyError,IndexError,OSError) as exc:
        print(json.dumps({"ok":False,"error":str(exc)}))
        sys.exit(1)
