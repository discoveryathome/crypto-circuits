# Original local cancellation-aware search toolkit

This preparation implements new code; it neither executes nor incorporates
upstream search code. Preparation outputs are prior knowledge for the timed
experiment and cannot earn discovery credit there.

## Run a session

From the pilot repository root:

```sh
python3 research/agent-pilot-v2/preparation/search/run_search.py \
  --spec portfolio/square-aes-mugi.json \
  --seed 123456789 --cpu-seconds 1200 --wall-seconds 1500 \
  --start certificates/square-aes-mugi--aes-mixcols-xor88-depth5-circ.json \
  --output research/agent-pilot-v2/SESSION-OUTPUT
```

Use start paths from the frozen session manifest. Repeat `--start` for
all reconciled starting witnesses. Omitting it loads the original specification's
baseline set, which may omit post-freeze literature corrections. **For the new
experiment explicitly supply its reconciled starts.**

Standard-library Python and a C++17 compiler are required. The wrapper compiles
only this directory's original `search.cpp` if its binary is absent or stale.
No network access, installation, upstream build, or remote write is performed.
The output directory must be new/empty, preventing accidental overwrite.

The seed is a recorded unsigned 64-bit integer. The core RNG is `mt19937_64`.
The same compiler/source, seed, starts, and operation count produce the same
candidate sequence. A CPU/wall cutoff may end at different iteration counts on
different machines; replay compares the common prefix rather than promising
identical time-cutoff outcomes. CPU budget is core process CPU time; wrapper
checking and compilation are separately incurred costs. The wall guard applies
to the search core. The current bounded operation may finish slightly beyond
the requested deadline. A supervising agent should also enforce its session
wall deadline. Raw checkpoints and progress are flushed while search runs.

Every reported Pareto point, including supplied starts, is immediately checked
by both `linear_pilot/checker.py` and `tools/audit_submission.py`. Candidate JSON,
SHA256, exact coordinates, source/binary hashes, start provenance, timings, and
checker evidence are checkpointed under the chosen output directory. Correctness
is not novelty; no discovery adjudication is performed by this program.

## Methods and limits

1. **Whole-map bounded-distance BP-style synthesis.** Maintain semantic binary
   coefficient vectors for all available signals and an explicit representation
   of every target. Enumerate all distinct semantic XOR combinations of up to
   three available signals, keeping their shortest representations. Evaluate
   every new two-signal XOR by the resulting upper bounds on target distances;
   minimize the sum, with seeded alternatives for squared-distance and depth
   tie-breaking. Current target expressions guarantee continuing progress when
   the three-signal bound is weak. This permits cancellations across signals
   with overlapping input support. Distances larger than three are heuristic
   upper bounds; this is **not a reproduction of SBP or exact canonical BP**.
2. **Exact-distance BP window resynthesis.** Select contiguous windows of
   3–20 gates with at most 16 incoming wires. Treat cut inputs as independent
   formal variables. Over their complete vector space update the exact shortest
   representation distance using
   `D_new(x) = min(D_old(x), 1 + D_old(x XOR new_signal))`. Select each new XOR
   greedily using those exact distances. Preserve every window wire used later,
   splice the replacement into the whole SLP, and accept only non-worsening
   gate count and output depth. This is exact **distance computation**, not
   exhaustive circuit synthesis or a proof that the window is optimal.
3. Track separate count/depth Pareto points, prune unused gates, and rotate
   among current frontier starts. Whole-map synthesis runs every 40 iterations;
   remaining iterations attempt windows. All gates remain binary XORs.

This implementation currently requires nonzero outputs, XOR-only starts with
integer wire references, and at most 63 primary inputs. It intentionally refuses
other formats rather than silently changing their gate model. Linear source
matrices and original input/output order remain fixed. The n32 method's triple
representation table grows cubically in available signals; large maps may spend
most time on a single synthesis. It is a useful stronger screening method, not
an assertion of state-of-the-art performance.

## Tests and preparation receipts

```sh
python3 research/agent-pilot-v2/preparation/search/test_toolkit.py
```

The original C++ tests check exact and bounded synthesis, explicit semantic
cancellation, deterministic seed replay, and 100 equivalent window replacements.
The two emitted example circuits then pass both independent checker
implementations. The example specification is fixed in the test rather than
inferred from the candidate. `tests.json` records results.

`smoke-aes/` is a 10-CPU-second operational preparation test: 159 completed
iterations, 78 window syntheses, three whole-map syntheses, no new Pareto point.
Its baseline and any future preparation candidates are not timed discoveries.
That smoke source predates warning-only edits; each receipt records exact hashes.
