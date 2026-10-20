"""Small, auditable search methods; not a reproduction of state-of-the-art BP.

Randomized common-subexpression synthesis, semantic resubstitution, and
single-fanout reassociation walks. Search never imports the trusted checker.
"""
import collections
import copy
import itertools
import random
from functools import lru_cache


def metrics(c):
    ds = [0] * c["inputs"]
    counts = dict(AND=0, XOR=0, NOT=0)
    for op, *args in c["gates"]:
        counts[op] += 1
        ds.append(1 + max(ds[a] if type(a) is int else 0 for a in args))
    return dict(counts, total=len(c["gates"]),
                depth=max((ds[a] if type(a) is int else 0 for a in c["outputs"]), default=0))


AXES = ("AND", "XOR", "total", "depth")


def dominates(a, b):
    return all(a[k] <= b[k] for k in AXES) and any(a[k] < b[k] for k in AXES)


def prune(c):
    n = c["inputs"]
    live = set(x for x in c["outputs"] if type(x) is int)
    for i in reversed(range(len(c["gates"]))):
        if n+i in live:
            live.update(x for x in c["gates"][i][1:] if type(x) is int)
    names = {i:i for i in range(n)}
    names.update({"0":"0", "1":"1"})
    gates = []
    for i, (op, *args) in enumerate(c["gates"]):
        if n+i in live:
            names[n+i] = n+len(gates)
            gates.append([op, *(names[x] for x in args)])
    return {"inputs":n, "gates":gates, "outputs":[names[x] for x in c["outputs"]]}


@lru_cache(maxsize=8)
def input_planes(n):
    size = 1 << n
    return tuple(int.from_bytes(bytes(sum(((8*k+b) >> i & 1) << b for b in range(8))
                                     for k in range((size+7)//8)), "little")
                 for i in range(n))


def signal_values(c, nonlinear=False):
    n = c["inputs"]
    if nonlinear:
        # Exhaustive truth tables as integers; independent of checker's oracle.
        size = 1 << n
        full = (1 << size)-1
        values = list(input_planes(n))
    else:
        full = 1 << n
        values = [1 << i for i in range(n)]
    def get(r):
        return values[r] if type(r) is int else (full if r == "1" else 0)
    for op, *args in c["gates"]:
        if op == "NOT":
            v = get(args[0]) ^ full
        elif op == "XOR":
            v = get(args[0]) ^ get(args[1])
        else:
            v = get(args[0]) & get(args[1])
        values.append(v)
    return values, full


def resubstitute(c, rng, nonlinear=False):
    """Try a random gate's equivalent earlier wire or alternate XOR pair."""
    if not c["gates"]:
        return c, False
    c = copy.deepcopy(c)
    n = c["inputs"]
    index = rng.randrange(len(c["gates"]))
    wire = n+index
    values, full = signal_values(c, nonlinear)
    lookup = {0:"0", full:"1"}
    ds = [0]*n
    for op, *args in c["gates"]:
        ds.append(1 + max(ds[a] if type(a) is int else 0 for a in args))
    for j in range(wire):
        v = values[j]
        if v not in lookup or (type(lookup[v]) is int and ds[j] < ds[lookup[v]]):
            lookup[v] = j
    target = values[wire]
    if target in lookup:
        replacement = lookup[target]
        for g in c["gates"][index+1:]:
            for k in range(1, len(g)):
                if g[k] == wire:
                    g[k] = replacement
        c["outputs"] = [replacement if x == wire else x for x in c["outputs"]]
        return prune(c), True
    candidates = []
    original = c["gates"][index]
    for j in range(wire):
        other = lookup.get(target ^ values[j])
        if other is not None:
            g = ["XOR", j, other]
            if g != original and g != [original[0], *reversed(original[1:])]:
                candidates.append(g)
    if not candidates:
        return c, False
    # Alternate decompositions enable neutral walks and changes to sharing.
    c["gates"][index] = rng.choice(candidates)
    return prune(c), True


def reassociate(c, rng):
    """(a XOR b) XOR z -> (a XOR z) XOR b, when the inner node is private."""
    n = c["inputs"]
    uses = collections.Counter(x for g in c["gates"] for x in g[1:] if type(x) is int)
    uses.update(x for x in c["outputs"] if type(x) is int)
    options = []
    for i, g in enumerate(c["gates"]):
        if g[0] != "XOR":
            continue
        for side in (1, 2):
            inner, z = g[side], g[3-side]
            if (type(inner) is int and inner >= n and uses[inner] == 1
                    and c["gates"][inner-n][0] == "XOR"
                    and (type(z) is str or z < inner)):
                options.append((i, inner-n, z))
    if not options:
        return c, False
    c = copy.deepcopy(c)
    i, j, z = rng.choice(options)
    a, b = c["gates"][j][1:]
    if rng.randrange(2):
        a, b = b, a
    c["gates"][j] = ["XOR", a, z]
    c["gates"][i] = ["XOR", n+j, b]
    return c, True


def paar(matrix, rng, depth_bias=False):
    """Randomized cancellation-free common-subexpression sharing from scratch."""
    n = len(matrix[0])
    rows = [{i for i, x in enumerate(row) if x} for row in matrix]
    gates = []
    depths = [0]*n
    while True:
        counts = collections.Counter(pair for row in rows for pair in itertools.combinations(sorted(row), 2))
        if not counts or max(counts.values()) < 2:
            break
        maximum = max(counts.values())
        choices = [p for p, count in counts.items() if count == maximum]
        if depth_bias:
            d = min(max(depths[a], depths[b]) for a, b in choices)
            choices = [p for p in choices if max(depths[p[0]], depths[p[1]]) == d]
        a, b = rng.choice(choices)
        new = n+len(gates)
        gates.append(["XOR", a, b])
        depths.append(1+max(depths[a], depths[b]))
        for row in rows:
            if a in row and b in row:
                row.difference_update((a, b))
                row.add(new)
    outputs = []
    for row in rows:
        pending = sorted(row, key=lambda x:(depths[x], x))
        if not pending:
            outputs.append("0")
            continue
        while len(pending) > 1:
            a, b = pending.pop(0), pending.pop(0)
            ref = n+len(gates)
            gates.append(["XOR", a, b])
            depths.append(1+max(depths[a], depths[b]))
            pending.append(ref)
            pending.sort(key=lambda x:(depths[x], x))
        outputs.append(pending[0])
    return prune({"inputs":n, "gates":gates, "outputs":outputs})


def walk(start, rng, steps, nonlinear=False):
    current = start
    frontier = [start]
    changes = 0
    for i in range(steps):
        candidate, changed = (reassociate(current, rng) if i % 3 == 0 else
                              resubstitute(current, rng, nonlinear))
        if not changed:
            continue
        m, old = metrics(candidate), metrics(current)
        # Neutral changes permitted, strict worsening never accepted.
        if all(m[k] <= old[k] for k in AXES):
            current = candidate
            changes += 1
            if not any(metrics(x) == m or dominates(metrics(x), m) for x in frontier):
                frontier = [x for x in frontier if not dominates(m, metrics(x))]
                frontier.append(candidate)
    return frontier, changes


def gf_mul(a, b, p, w=4):
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a >> w:
            a ^= p
    return result


def word_matrix_to_bits(a, w=4, p=0x13):
    return [[(gf_mul(a[i//w][j//w], 1 << (j%w), p, w) >> (i%w)) & 1
             for j in range(len(a)*w)] for i in range(len(a)*w)]


def published_mds(involutory=False):
    """Tian--Feng--Li 2024, table 6 #17; section 3.5 tree 3 assignment 4.

    Instantiate the 4-bit companion operation for x^4+x+1. Shared scalar
    multiplications are emitted once. Both MDS and involution are checked.
    """
    gates = []
    def xor(a, b):
        gates.append(["XOR", a, b])
        return 16+len(gates)-1
    def add(a, b):
        return [xor(x,y) for x,y in zip(a,b)]
    def mulx(a):
        return [a[3], xor(a[0],a[3]), a[1], a[2]]
    def divx(a):
        return [xor(a[1],a[0]), a[2], a[3], a[0]]
    a,b,c,d = [list(range(4*i,4*i+4)) for i in range(4)]
    if not involutory:
        x5 = add(a,b)
        x6 = add(c,d)
        y1 = add(x5,mulx(x6))
        x8 = add(a,x6)
        x9 = add(c,divx(x8))
        y2 = add(mulx(x5),x9)
        y3 = add(y1,x9)
        y4 = add(x8,y2)
        outputs = y1+y2+y3+y4
    else:
        x5 = add(a,b)
        x6 = add(x5,c)
        y1 = add(x6,d)
        x7 = add(a,mulx(x6))
        scaled7 = mulx(x7)
        x8 = add(y1,scaled7)
        y2 = add(c,x8)
        y3 = add(divx(x5),mulx(x8))
        y4 = add(scaled7,y3)
        outputs = y3+y4+y1+y2
    return {"inputs":16,"gates":gates,"outputs":outputs}
