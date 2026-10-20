# Gate model and verification

Every certificate is JSON with exactly `inputs`, `gates`, `outputs`. The
specification is a separate, trusted file in `portfolio/`, hashed in the plan.
Never accept a submitter's replacement specification.

```json
{"inputs":2,"gates":[["XOR",0,1]],"outputs":[2,0]}
```

Input wires are integers `0..inputs-1`. Gate `i` defines wire `inputs+i`.
References must name earlier wires. Strings `"0"` and `"1"` are free constants;
integers `0` and `1` name wires. XOR and AND have exactly two inputs; NOT has one.
Fanout and wire permutations are free; each gate costs one and adds one delay.
All declared gates are charged, including dead gates. Output depth is the longest
gate path to a designated output. No memory, table operations, macros, implicit
arithmetic, forward references, self references, float/bool indices, extra
fields, duplicate JSON keys or unknown operations are permitted.

XNOR expands to XOR followed by NOT. A ternary XOR expands to two binary XORs;
its optimal association and depth must be evaluated explicitly. No hardware
gate-equivalent, weighted h-XOR, free complement or quantum-depth headline
is copied into our frontier.

An in-place s-XOR/CNOT assignment `x[j] ^= x[i]` becomes a fresh SSA XOR node,
and subsequent uses of `x[j]` reference that node. Its gate count transfers.
Classical free-fanout depth is recomputed and may differ from quantum depth,
where reads and writes sharing a wire cannot operate simultaneously.

## Primary checker

`linear_pilot/checker.py` imports neither search nor source-importer code.

- **Fixed linear maps:** rejects AND gates, then propagates exact affine
  coefficients as sets. Every output coefficient equals the separate published
  matrix and the affine constant is zero. This proves equality on all inputs,
  including the 128-bit ARIA instance. Testing basis vectors alone would not
  prove equality for an unrestricted nonlinear program.
- **Multipliers:** enumerates all `2^(2m)` inputs, from 256 to 65,536 pairs.
  Expected outputs use polynomial convolution followed by long division by
  the fixed modulus. Circuit evaluation uses packed exhaustive truth tables.
  All XOR/AND/NOT programs are permitted; no bilinearity assumption is needed.
- **Diffusion design:** derives the exact binary matrix, checks every square
  block minor for full binary rank (69 minors), and checks `M*M=I` when required.
  This proves word branch number five on four 4-bit words. General binary
  blocks are allowed; field-linearity is not asserted or needed.

## Second implementation

`tools/audit_submission.py` imports no pilot code. It implements its own
structure checks and scalar gate evaluator.

- Linear circuits: rejects AND, checks zero and all basis vectors exactly.
- Multipliers: evaluates every pair against shift-and-reduce field arithmetic,
  independent of the primary checker's convolution/long-division oracle.
- Designs: evaluates all 65,536 inputs, checks the actual minimum word branch
  number, and verifies involution by composition when required.

This is independence of implementation, not independence of authorship. Both
checkers need external review before donor intake. A valid certificate proves
function and cost, not global optimality, novelty, resistance to side channels,
or security of a cipher incorporating a new diffusion layer.

Both scripts enforce a 2 MB file and 10,000-gate limit. Run expensive checks
with a process timeout. Source importers are never part of submission execution.
The test suite exercises wrong functions, bad references, unsupported lookup
operations, malformed gates, constants, dead-gate accounting, design properties
and search equivalence.

## Source conventions

The NIST matrix files are independently parsed row-major as `y=Mx`. Old NIST
linear circuits use one-based port names; internal references become zero-based.
AES MixColumns' current files use LSB-first byte bits; within-byte reversal is
applied only if the full old matrix comparison requires it, and that adapter
is recorded in baseline provenance. Nothing weaker than exact matrix equality
passes.

Xu--Sun CNOT files contain pairs on every line, including the last line. Their
final output wiring is recovered by matching the final signal coefficients to
the separately published matrix; no function or gate is added. The normalized
certificate then passes both independent checkers.
