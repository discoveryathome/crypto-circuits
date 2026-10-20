# Independent wave 1 review

**Accept five final points for the private experiment; leave one unresolved.**
This is a separate-agent literature and lineage adjudication, not external
scientific confirmation or a universal world-record guarantee. All six finalists
were freshly accepted by both trusted checker implementations. AES produced no
new submitted point. Superseded checkpoints do not receive separate credit.

| Fixed map | XOR / classical depth | Verdict | Exact scope |
|---|---:|---|---|
| Whirlwind M0 | 157 / 12 | Accepted | Count upper bound improves 159; also improves the known internal depth13 construction |
| Whirlwind M0 | 161 / 11 | Accepted | Nondominated size/depth tradeoff against audited published and internal prior |
| Whirlwind M0 | 163 / 10 | Accepted | Same tradeoff scope |
| Whirlwind M0 | 170 / 9 | Accepted | Same tradeoff scope |
| Whirlwind M0 | 209 / 7 | Unresolved; zero credit | Unknown-depth 172/173 and historical183-XOR comparators could dominate |
| Whirlwind M1 | 166 / 10 | Accepted | Count upper bound improves169; depth improves11 |

All points have AND=NOT=0 and total=XOR. `wave1-adjudication.json` contains full
candidate paths/hashes, fresh checker results and timings, comparator decisions,
and semantic graph comparisons. Credit is five final frontier points on two
instances; it is not five independent scientific breakthroughs or five sessions.

## Positive evidence supporting acceptance

[Xu and Sun's current primary paper](https://arxiv.org/html/2511.18226v2),
Table4, identifies Whirlwind M0/M1 constructions at159/169 XORs and compares
previous g-XOR and s-XOR results. These in-place circuits also give upper bounds
in the more permissive classical straight-line-program model. Their released
artifacts normalize to classical depths14/11. The arXiv version history still
ends atMay24,2026. A fresh read of the
[current artifact repository](https://github.com/DerryAlex/circulant_synth)
returns the same pinned head and source circuits. The downloaded receipts and
hashes are in `wave1-source-receipts.json`; no upstream code was executed.

The [October17 GPU preprint](https://eprint.iacr.asia/2026/2520) gives172/170
XOR claims. Those counts cannot dominate any of the five accepted candidates,
regardless of their missing depths. The historical M0 173/183 and M1 180/181
comparators likewise have strictly larger XOR counts. The 209/7 proposal does
not pass this test and remains unresolved. The accessible
[new October9 diffusion-design paper](https://journal.hep.com.cn/fcs/EN/10.1007/s11704-026-61358-3)
describes newly designed matrices; its abstract supplies no exact Whirlwind
comparator. It is a literature lead, not grounds to invent a new baseline.

The frozen published and earlier local witnesses were compared point by point.
No accepted candidate is equal to or dominated by any. Search queries for later
Whirlwind results were also performed, but absence of a search hit is explicitly
not the basis of the verdict. Acceptance rests on the identified publication
lineage, exact artifacts and mathematical comparisons, with the usual limitation
that an audit cannot prove absence of all unpublished or unindexed work.

## Substantive construction versus baseline maintenance

The published size witnesses contain no dead gates or duplicate semantic nodes.
The M0 157/12 certificate contains37 intermediate linear forms absent from the
published159-gate witness and omits39 old forms; only93 gate equations are shared.
The M1 166/10 certificate introduces52 forms, omits55, and shares78 equations.
This demonstrates changed computation graphs, not renumbering, output rewiring,
CNOT-to-SSA conversion, or cleanup of already unused gates. The three accepted M0
tradeoffs likewise introduce43–72 new forms relative to the published witness.
Session receipts identify adaptive semantic DAG rewriting and cut resynthesis.

The methods use established algebraic identities. No new optimizer theory is
claimed. The result being credited is an improved exact circuit construction
under the frozen general binary-XOR model. These witnesses do not establish
improved in-place CNOT circuits, quantum schedules, hardware area, optimality,
or security of an entire cryptographic function.

## Review costs and limits

Review began2026-10-20T06:52:02Z. The JSON records completion time and total
reviewer elapsed seconds. Fresh per-point mechanical review and checker times
are individually instrumented. Literature work was shared across the packet;
per-point literature time is unavailable and is not artificially allocated.
The checks operate on certificate data, not submission programs. No optimization
search was performed during review.

The independent reviewer is another agent in the same model family and uses the
two existing trusted checker implementations. External scientific review remains
outstanding. All correct candidates, including209/7, should become known prior
for wave2; only the five accepted points earn current experiment credit.
