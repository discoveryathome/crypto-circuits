"""Trusted checker. No imports from search, builders, or source importers.

Linear certificates are proved by affine coefficient propagation, not sampling.
Multiplier certificates are evaluated on every input pair against polynomial
convolution and long division. Design certificates additionally prove all block
minors nonsingular. JSON is data only; no expressions are evaluated.
"""
import itertools
import json
import pathlib
import time


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def read_json(path):
    p = pathlib.Path(path)
    require(p.stat().st_size <= 2_000_000, "file exceeds 2 MB")
    def unique(pairs):
        d = {}
        for k, v in pairs:
            require(k not in d, "duplicate JSON key")
            d[k] = v
        return d
    return json.loads(p.read_text(), object_pairs_hook=unique)


def structure(c, inputs, outputs, linear):
    require(type(c) is dict and set(c) == {"inputs", "gates", "outputs"},
            "certificate must contain exactly inputs, gates, outputs")
    require(type(c["inputs"]) is int and c["inputs"] == inputs, "input count")
    require(type(c["gates"]) is list and len(c["gates"]) <= 10000, "gate limit")
    require(type(c["outputs"]) is list and len(c["outputs"]) == outputs, "output count")
    depths = [0] * inputs
    counts = dict(AND=0, XOR=0, NOT=0)
    def ref(x, limit):
        require((type(x) is int and 0 <= x < limit) or
                (type(x) is str and x in ("0", "1")), "invalid/forward reference")
    for i, gate in enumerate(c["gates"]):
        require(type(gate) is list and len(gate) in (2, 3), "gate shape")
        op = gate[0]
        require(type(op) is str and op in counts, "unsupported operation")
        require(not linear or op != "AND", "linear profile requires AND=0")
        require(len(gate) == (2 if op == "NOT" else 3), "gate arity")
        for r in gate[1:]:
            ref(r, inputs + i)
        depths.append(1 + max(depths[r] if type(r) is int else 0 for r in gate[1:]))
        counts[op] += 1
    for r in c["outputs"]:
        ref(r, len(depths))
    live = set(r for r in c["outputs"] if type(r) is int)
    for i in reversed(range(len(c["gates"]))):
        if inputs + i in live:
            live.update(r for r in c["gates"][i][1:] if type(r) is int)
    return dict(counts, total=len(c["gates"]),
                depth=max((depths[r] if type(r) is int else 0 for r in c["outputs"]), default=0),
                dead_gates=sum(inputs + i not in live for i in range(len(c["gates"]))))


def affine_outputs(c):
    # Sets of variable indices; -1 is the affine constant. Independent of the
    # integer bitmask representation used by synthesis.
    values = [frozenset([i]) for i in range(c["inputs"])]
    def get(r):
        return values[r] if type(r) is int else frozenset([-1] if r == "1" else [])
    for g in c["gates"]:
        values.append(get(g[1]) ^ (frozenset([-1]) if g[0] == "NOT" else get(g[2])))
    return [get(r) for r in c["outputs"]]


def rank(rows, width):
    a = [list(r) for r in rows]
    pivot = 0
    for col in range(width):
        found = next((j for j in range(pivot, len(a)) if a[j][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        for j in range(pivot + 1, len(a)):
            if a[j][col]:
                a[j] = [x ^ y for x, y in zip(a[j], a[pivot])]
        pivot += 1
    return pivot


def design_properties(rows, involutory):
    # Four words of four bits. A block MDS linear map has branch number 5 iff
    # all square block submatrices are nonsingular (69 minors, including full).
    require(len(rows) == 16 and all(len(r) == 16 for r in rows), "design size")
    minors = 0
    for size in range(1, 5):
        for rs in itertools.combinations(range(4), size):
            for cs in itertools.combinations(range(4), size):
                sub = [[rows[4*r+i][4*c+j] for c in cs for j in range(4)]
                       for r in rs for i in range(4)]
                require(rank(sub, 4*size) == 4*size, "not block MDS")
                minors += 1
    if involutory:
        for i in range(16):
            for j in range(16):
                require(sum(rows[i][k] * rows[k][j] for k in range(16)) % 2 == int(i == j),
                        "matrix is not involutory")
    return {"block_minors": minors, "branch_number": 5, "involutory_required": involutory}


def polynomial_product(a, b, modulus, width):
    # Direct convolution then long division, deliberately different from
    # synthesis's shift-and-reduce multiplier.
    coefficients = [0] * (2*width - 1)
    for i in range(width):
        for j in range(width):
            coefficients[i+j] ^= ((a >> i) & 1) & ((b >> j) & 1)
    for i in range(2*width - 2, width - 1, -1):
        if coefficients[i]:
            for j in range(width + 1):
                coefficients[i-width+j] ^= (modulus >> j) & 1
    return sum(coefficients[i] << i for i in range(width))


def exhaustive_multiplier(c, width, modulus):
    # One bit position per (a,b); every possible pair is represented.
    points = 1 << (2*width)
    mask = (1 << points) - 1
    planes = [bytearray((points+7)//8) for _ in range(2*width)]
    expected = [bytearray((points+7)//8) for _ in range(width)]
    for point in range(points):
        for j in range(2*width):
            if (point >> j) & 1:
                planes[j][point//8] |= 1 << (point % 8)
        value = polynomial_product(point & ((1 << width)-1), point >> width, modulus, width)
        for j in range(width):
            if (value >> j) & 1:
                expected[j][point//8] |= 1 << (point % 8)
    values = [int.from_bytes(x, "little") for x in planes]
    def get(r):
        return values[r] if type(r) is int else (mask if r == "1" else 0)
    for op, *args in c["gates"]:
        if op == "NOT":
            value = get(args[0]) ^ mask
        elif op == "XOR":
            value = get(args[0]) ^ get(args[1])
        else:
            value = get(args[0]) & get(args[1])
        values.append(value)
    require(all(get(r) == int.from_bytes(v, "little") for r, v in zip(c["outputs"], expected)),
            "incorrect field multiplication")
    return {"exhaustive_inputs": points}


def verify(c, spec):
    start = time.perf_counter()
    kind = spec["kind"]
    require(kind in ("linear", "multiplier", "design"), "unknown specification")
    n = spec["inputs"]
    m = spec["outputs"]
    metrics = structure(c, n, m, kind != "multiplier")
    if kind == "multiplier":
        evidence = exhaustive_multiplier(c, spec["width"], spec["modulus"])
    else:
        result = affine_outputs(c)
        require(all(-1 not in s for s in result), "nonzero affine constant")
        rows = [[int(j in s) for j in range(n)] for s in result]
        if kind == "linear":
            require(rows == spec["matrix"], "incorrect linear transformation")
            evidence = {"coefficient_equalities": n*m, "proof": "exact affine propagation"}
        else:
            evidence = design_properties(rows, spec["involutory"])
            evidence["matrix"] = rows
    return {"ok": True, "metrics": metrics, "evidence": evidence,
            "verification_seconds": time.perf_counter() - start}
