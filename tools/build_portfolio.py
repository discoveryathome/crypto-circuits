#!/usr/bin/env python3
"""Parse pinned public artifacts as data, verify, then freeze specifications."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from linear_pilot.checker import verify, Invalid
from linear_pilot.synthesis import published_mds, signal_values


def write(path, data):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse_nist(path):
    text = path.read_text()
    def ports(label):
        match = re.search(label+r":\s*([xy])(\d+):[xy](\d+)", text)
        prefix, lo, hi = match.groups()
        return [prefix+str(i) for i in range(int(lo), int(hi)+1)]
    ins, outs = ports("Inputs"), ports("Outputs")
    wires = {name:i for i, name in enumerate(ins)}
    gates = []
    body = text.split("begin SLP")[1].split("end SLP")[0]
    for line in body.splitlines():
        line = line.split("#")[0].split("%")[0].strip()
        if not line:
            continue
        op, target, *args = line.split()
        if target in wires or op not in ("XOR", "EQUAL", "AND", "XNOR"):
            raise ValueError("unexpected source operation")
        if op == "EQUAL":
            assert len(args) == 1
            wires[target] = wires[args[0]]
        else:
            assert len(args) == 2
            g = ["XOR" if op == "XNOR" else op, *(wires[a] for a in args)]
            gates.append(g)
            wires[target] = len(ins)+len(gates)-1
            if op == "XNOR":
                gates.append(["NOT", wires[target]])
                wires[target] = len(ins)+len(gates)-1
    return {"inputs":len(ins), "gates":gates, "outputs":[wires[x] for x in outs]}


def parse_multiplier(path, width):
    wires = {letter+str(i):i+offset for letter, offset in (("A",0),("B",width))
             for i in range(width)}
    gates = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        match = re.fullmatch(r"([TC]\d+)\s*=\s*([ABTC]\d+)(?:\s*([+X])\s*([ABTC]\d+))?", line.upper())
        if not match:
            raise ValueError("unrecognized multiplier source syntax")
        dst, a, op, b = match.groups()
        assert dst not in wires
        if op:
            gates.append(["XOR" if op == "+" else "AND", wires[a], wires[b]])
            wires[dst] = 2*width+len(gates)-1
        else:
            wires[dst] = wires[a]
    return {"inputs":2*width,"gates":gates,"outputs":[wires["C"+str(i)] for i in range(width)]}


def parse_cnot(path, matrix):
    # All lines are CNOT pairs. Recover the output permutation by exact signal
    # matching to the separately published matrix (free output wiring).
    n = len(matrix)
    lines = [list(map(int, l.split())) for l in path.read_text().splitlines() if l.strip()]
    wires = list(range(n))
    gates = []
    for line in lines:
        assert len(line) % 2 == 0
        for a, b in zip(line[::2], line[1::2]):
            gates.append(["XOR", wires[a], wires[b]])
            wires[b] = n+len(gates)-1
    c = {"inputs":n,"gates":gates,"outputs":wires}
    values, _ = signal_values(c)
    targets = [sum(bit << i for i, bit in enumerate(row)) for row in matrix]
    finals = {values[wire]:wire for wire in wires}
    c["outputs"] = [finals[v] for v in targets]
    return c


def main():
    nist = ROOT/"sources/nist/data/slp/2021-linearmaps"
    files = sorted((nist/"matrices").glob("ciphers-*/*.mat.txt"))
    names = ["BKL16-4x4-GF16", "JPST17-4x4-GF16", "KLSW17-M-4x4-GF16", "LS16-4x4-GF16"]
    files += [nist/"matrices/mds-4x4-GF16"/(x+".mat.txt") for x in names]
    assert len(files) == 24
    entries, reports = [], []
    def baseline(entry, c, origin, label):
        result = verify(c, entry)
        rel = "certificates/"+entry["id"]+"--"+slug(label)+".json"
        write(rel, c)
        entry["baselines"].append({"path":rel,"origin":origin,"metrics":result["metrics"],
                                   "status":"independently-checked-code; not external review"})
        reports.append({"instance":entry["id"],"path":rel,**result})
    for f in files:
        name = f.name.removesuffix(".mat.txt")
        raw = list(map(int, f.read_text().split()))
        assert raw[0] == 1
        m, n = raw[1:3]
        assert m == n and len(raw[3:]) == m*n
        # Separate matrix files define y=Mx, row-major. The checker compares
        # every coefficient, independently of circuit header metadata.
        matrix = [[raw[3+i*n+j] for j in range(n)] for i in range(m)]
        entry = dict(id=slug(name),title=name,kind="linear",inputs=n,outputs=m,
                     matrix=matrix,matrix_source=str(f.relative_to(ROOT)),
                     baselines=[],use="published cryptographic diffusion benchmark",
                     literature_status="audited corpus; global completeness not certified")
        source = next((nist/"circuits"/f.parent.name).glob(name+"--*.circ.txt"))
        baseline(entry, parse_nist(source), str(source.relative_to(ROOT)), "nist")
        # Current 2026 AES layer artifacts use conventional LSB-per-byte ports.
        if name == "Square+AES+Mugi":
            for src in sorted((ROOT/"sources/nist/data/slp/aes/aes-mixcols").glob("aes-mixcols-*.circ.txt")):
                c = parse_nist(src)
                try:
                    baseline(entry,c,str(src.relative_to(ROOT)),src.stem)
                except Invalid:
                    # Explicit, reversible bit permutation: old benchmark ports
                    # are MSB-first within each byte.
                    perm = [8*(i//8)+7-i%8 for i in range(32)]
                    c["gates"] = [[g[0], *(perm[x] if type(x) is int and x < 32 else x
                                           for x in g[1:])] for g in c["gates"]]
                    c["outputs"] = [c["outputs"][perm[i]] for i in range(32)]
                    baseline(entry,c,str(src.relative_to(ROOT))+"; bit reversal within bytes",src.stem)
        if name in ("WhirlwindM0", "WhirlwindM1"):
            fname = name.replace("M","_M")+".txt"
            for lane in ("size","depth"):
                src = ROOT/"sources/circulant/results"/lane/fname
                c = parse_cnot(src, matrix)
                baseline(entry,c,str(src.relative_to(ROOT))+"; CNOT to SSA; exact output permutation", "xu2026-"+lane)
        entries.append(entry)
    jain = ROOT/"sources/jain/multipliers/circuits"
    for width, p, names in [
        (4,0x13,["final_f4"]), (5,0x25,["final_f5"]), (6,0x49,["final_f6"]),
        (7,0x89,["final_f73","final_f73_d6"]), (7,0x91,["final_f7"]),
        (8,0x11b,sorted(x.stem for x in jain.glob("aes*.slp")))
    ]:
        entry = dict(id=f"gf{width}-{p:x}",title=f"GF(2^{width}), modulus {hex(p)}",
                     kind="multiplier",inputs=width*2,outputs=width,width=width,modulus=p,
                     baselines=[],use="polynomial-basis multiplication component",
                     literature_status="Jain October 2026 plus CMT; no global optimality claim")
        for name in names:
            src = jain/(name+".slp")
            baseline(entry,parse_multiplier(src,width),str(src.relative_to(ROOT)),name)
        # Strong historical points matter on the AND/XOR/depth frontier.
        old = {6:"slp_630.txt",7:"slp_740.txt",8:"slp_84310.txt"}
        if width in old and p != 0x89:
            src = ROOT/"sources/jain/multipliers/sources/circuits/cmt"/old[width]
            baseline(entry,parse_multiplier(src,width),str(src.relative_to(ROOT)),"cmt")
        entries.append(entry)
    for involutory in (False, True):
        entry = dict(id="design-mds4x4-w4"+("-involution" if involutory else ""),
                     title="4x4 block MDS on four 4-bit words"+("; involutory" if involutory else ""),
                     kind="design",inputs=16,outputs=16,involutory=involutory,baselines=[],
                     use="branch-number-5 diffusion design, GL(4,2) blocks; not a full cipher security claim",
                     literature_status="35/36-XOR constructions published; general optimality unproved")
        baseline(entry,published_mds(involutory),
                 "https://arxiv.org/html/2409.03298v1; table 6 #17 / section 3.5 tree 3 #4; 4-bit instantiation",
                 "tian2024")
        if involutory:
            # Pick an actually involutory published witness, never silently relax.
            for src in sorted((nist/"circuits/mds-4x4-GF16").glob("*.circ.txt")):
                c = parse_nist(src)
                try:
                    verify(c,entry)
                except Invalid:
                    continue
                baseline(entry,c,str(src.relative_to(ROOT)),src.stem)
        assert entry["baselines"], entry["id"]
        entries.append(entry)
    assert len(entries) == 32
    for entry in entries:
        write("portfolio/"+entry["id"]+".json",entry)
    write("portfolio/index.json",{"instances":[e["id"] for e in entries],
                                  "count":len(entries),"basis":["XOR","AND","NOT","0","1"],
                                  "axes":["AND","XOR","total","depth"]})
    write("results/baseline-verification.json",reports)
    print("Verified",len(reports),"published witnesses over",len(entries),"instances")


if __name__ == "__main__":
    main()
