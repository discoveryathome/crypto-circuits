# Independent checking and novelty

Submit a JSON circuit plus a receipt containing the instance ID, seed,
starting-circuit hash, exact work and time budget, method version, candidate
hash and claimed `(AND, XOR, total, depth)`. For matrix design also state the
constraints and output matrix. Only data certificates are accepted.

From this trusted checkout:

```sh
python3 -I tools/check_submission.py portfolio/INSTANCE.json /path/to/candidate.json
python3 -I tools/audit_submission.py portfolio/INSTANCE.json /path/to/candidate.json
```

Check the specification hash against `results/plan.json`. Do not let a submitted
program select a different matrix, modulus, bit order or gate basis.

Acceptance requires:

1. Both independent checker implementations agree on exact function and metrics.
2. The candidate is nondominated against the reconciled published frontier.
   Retain the native model and conversion record for each comparator.
3. Resolve stronger count-only literature claims, including missing witnesses,
   output conventions and depth assumptions. Equal coordinates do not create
   a new frontier point. A smaller XOR count with more ANDs is a tradeoff,
   not an AND-count improvement.
4. Search the paper/artifact lineage and check duplicates before assigning
   novelty. Straightforward replication or rebalancing of a published component
   is baseline maintenance unless a substantive new claim is established.
5. Record a candidate-specific adjudication with source links, the exact scope
   of the improvement and verification timings. External review is separate
   from the two local implementations.

Examples in `results/candidates/` are correct constructions, not a list of
new discoveries. `results/proposals.json` identifies corpus proposals;
`results/novelty-audit.json` explains their status. Do not promote every
unreported tradeoff into a new world record. A larger set of downloaded
baselines is not evidence of exhaustive worldwide coverage.

For diffusion design, a new matrix byte string or an output permutation at the
same cost is not progress. New MDS matrices also do not imply a secure cipher.
The experiment's two design tasks fix dimensions, branch number, bit model,
and involution requirement in advance. Do not add bespoke constraints after
finding a candidate to create an easier leaderboard.

No automatic frontier publication, git push, message sending, or hub submission
is implemented. Store proposals locally for review. Intake opened on 21 October 2026 under the recorded maintainer decision.
External scientific review remains pending; use CONTRIBUTOR_WORKFLOW.md for current targets.
