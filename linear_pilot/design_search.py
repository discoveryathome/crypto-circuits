"""Bounded sampling of established circulant / Hadamard GF16 families.

New matrix bytes alone are NOT discoveries. Only audited cost/depth advances
qualify. The independent checker uses binary block ranks, not this field test.
"""
import itertools
from .synthesis import gf_mul, word_matrix_to_bits, paar


def field_rank(matrix):
    a = [r[:] for r in matrix]
    k = len(a)
    for i in range(k):
        pivot = next((j for j in range(i,k) if a[j][i]),None)
        if pivot is None:
            return False
        a[i],a[pivot] = a[pivot],a[i]
        inv = next(x for x in range(1,16) if gf_mul(a[i][i],x,0x13) == 1)
        a[i] = [gf_mul(x,inv,0x13) for x in a[i]]
        for j in range(i+1,k):
            scalar = a[j][i]
            a[j] = [x ^ gf_mul(scalar,y,0x13) for x,y in zip(a[j],a[i])]
    return True


def is_mds(a):
    for k in range(1,5):
        for rs in itertools.combinations(range(4),k):
            for cs in itertools.combinations(range(4),k):
                if not field_rank([[a[r][c] for c in cs] for r in rs]):
                    return False
    return True


def sample(rng, draws, involutory):
    candidates = []
    valid = 0
    seen = set()
    for _ in range(draws):
        row = [rng.randrange(1,16) for _ in range(4)]
        if involutory:
            # Hadamard square = sum(row)^2 * I, hence choose sum(row)=1.
            row[3] = 1 ^ row[0] ^ row[1] ^ row[2]
            a = [[row[i ^ j] for j in range(4)] for i in range(4)]
        else:
            a = [[row[(j-i) % 4] for j in range(4)] for i in range(4)]
        key = tuple(x for r in a for x in r)
        if key in seen:
            continue
        seen.add(key)
        if not is_mds(a):
            continue
        valid += 1
        candidates.append(paar(word_matrix_to_bits(a),rng,True))
    return candidates, {"draws":draws,"distinct_matrices":len(seen),"mds_matrices":valid}
