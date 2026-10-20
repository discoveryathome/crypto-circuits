# Local validation

The executable release was tested from a fresh `git archive` of
`5f0de7eed15b2186fb52d34c6174fed1269c9231`, in a temporary directory with no
network or installation step. Python 3.14.6 was used. The code uses Python 3.9+
standard-library features, but older interpreters were not tested here.

- All 10 tests passed, including malformed references, unknown operations,
  hidden fields, duplicate JSON keys, wrong functions, nonlinear gates in
  affine proofs, incorrect products, non-MDS designs and wrong involution.
- `tools/check_all.py` passed 391 certificate/specification checks in 49.64
  seconds. It also checked all frozen file hashes, 451 retained source hashes,
  and agreement with the archived second-check metrics.
- Both checker executables independently accepted the depth-5, 44-gate GF32
  transformation over all 1,024 inputs.
- Isolated deterministic replays matched every retained candidate hash for
  Joltik wave 1, GF256 wave 2, and MDS design wave 1. CLI waves are zero-indexed.
  Timing equality was excluded.
- Every one of the 70 corpus proposals and one baseline per instance passed
  the standalone checker. Additional SBP and ARIA prior certificates also
  passed both implementations; their receipts are separate.

Full commands, outputs and timing records are in
[fresh-check.json](../results/fresh-check.json). Later commits add only these
validation records and documentation unless a subsequent change says otherwise.
The original plan and every file it hashes remain unchanged.

Required protocol fields, catalogue weights, and local documentation links were
checked. This was not a full JSON-Schema conformance run. The manifest
intentionally lacks a consenting maintainer, so it does not satisfy the public
registration schema and donor intake stays paused.

These are local implementation checks, not external scientific review. No claim
of novel mathematics, global optimality or actual donated-agent productivity
follows from them.
