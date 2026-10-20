# Preparation audit, 2026-10-20

Select **AES MixColumns (`square-aes-mugi`), Whirlwind M0, and Whirlwind M1**.
These are existing useful fixed maps, not newly invented easy matrices. All have
published binary-XOR witnesses; the last two also test whether structural methods
beat the current compact implementations. The selection does not imply an easy
expected discovery rate. This work is preparation, outside the six session clocks.

`comparators.json` contains 45 freshly checked records: every selected published
baseline, every saved prior local trial candidate, and the two additional AES
normalizations below. Each includes a certificate hash, full metrics, provenance,
and results from both checker implementations. Prior local constructions are
ineligible for new-session discovery credit even where their novelty is unresolved.

| Instance | Retrieved published frontier `(XOR,depth)` | Combined known frontier |
|---|---|---|
| AES MixColumns | `(88,5), (90,4), (97,3)` | Same |
| Whirlwind M0 | `(159,14)` | `(159,13), (217,5)` |
| Whirlwind M1 | `(169,11)` | `(169,11), (240,5)` |

AND=NOT=0 and total=XOR for these points. The table is an artifact-backed frontier,
not a claim of complete worldwide depth coverage. Depth is classical free-fanout,
unit-delay binary-gate depth. Quantum scheduling depth and hardware GE are separate.

## Sources and normalization

- [NIST catalogue](https://csrc.nist.gov/projects/circuit-complexity/list-of-circuits)
  supplies the three current AES witnesses. Fresh GitHub tree receipts confirm
  NIST commit `8366158a4324ef902ce740f29ddc9f7ebb1018b2`, unchanged from the first
  pilot. All selected circuit hashes and matrix specifications are retained.
- [Xu and Sun, May 2026 revision](https://arxiv.org/html/2511.18226v2), with
  [artifact repository](https://github.com/DerryAlex/circulant_synth), supplies
  159/169-XOR Whirlwind implementations. In-place CNOT assignments become SSA
  XOR nodes; output permutation and full map equality were checked. Their reported
  quantum depth does not transfer. Fresh repository head remains
  `73ff05008ae1d9445a69bc792653726cdccdca5b`.
- [HILL, ToSC 2026(1)](https://doi.org/10.46586/tosc.v2026.i1.506-526), Table 9,
  was reproduced from the indexed author-uploaded primary paper on
  [ResearchGate](https://www.researchgate.net/publication/402331700_HILL_Efficient_Low-Latency_Implementations_of_Linear_Layers_via_Heuristic_Search).
  The table has **59 binary and 20 ternary XOR gates**. The literal transcription
  is `hill-table9.txt`; `convert_hill.py` expands each gate using smallest-arrival
  inputs first. The resulting **99 binary XOR, depth 3** circuit passes both
  checkers in original port order. NIST `(97,3)` dominates it. This resolves the
  earlier pilot's missing normalization for this headline construction. Whirlwind
  is absent from the full indexed HILL text. Direct HTML download returned 403;
  no access-control bypass was attempted.
- [Pehlivanoğlu and Demir, 2024](https://doi.org/10.7717/peerj-cs.1820),
  [released mixed-fanin AES artifact](https://github.com/demirmehmet0/SBP/blob/f3880c8f87085e3eead3029593cee781e94ee60a/dB_BDKCI/results/depth-bounded%20BDKCI/ciphers_depth-bounded%20BDKCI/AES_240_95_depth-bounded%20BDKCI.txt):
  **5 XOR2 + 7 XOR3 + 32 XOR4** normalize to **115 binary XOR, depth 5**.
  Both checkers accept the converted certificate. Fresh repository head remains
  `f3880c8f87085e3eead3029593cee781e94ee60a`. Its released SBP binary section
  contains no Whirlwind witness. Mixed-fanin count 44 is not a binary count.

The HILL table and SBP conversion are baseline maintenance, not session discoveries.
No upstream optimizer or downloaded executable code was run.

## Unresolved comparators and strict credit rule

[Sun, Yang and Li, 2025/1493](https://eprint.iacr.org/2025/1493) reports an
89-XOR AES circuit in its revised abstract; its classical depth remains unknown
here. The [October 17 GPU preprint](https://eprint.iacr.asia/2026/2520) reports
172/170-XOR Whirlwind M0/M1 circuits, again without depth in the accessible
abstract. PDF retrieval returned 403. [Yuan et al. 2024](https://doi.org/10.46586/tosc.v2024.i2.322-347)
and [Xiang et al. 2020](https://doi.org/10.13154/tosc.v2020.i2.120-145)
also supply historical count guards encoded in `comparators.json`.

A missing depth is **null**, never infinity or the depth of another circuit.
For conservative screening, an unresolved count guard blocks a candidate whose
XOR count is at least that guard, unless a candidate-specific audit resolves the
comparison. Thus candidates with at most 88 AES, 171 M0, or 169 M1 XORs clear
these particular count-only blockers; they must still strictly advance the
combined known frontier and pass a lineage/novelty audit. Larger shallow
constructions remain correct proposals but receive no confirmed discovery credit
merely because their missing comparator depths were inconvenient.

These rules do not restrict which Pareto points may be searched or saved. They
restrict when discoveries can be credited. Equal coordinates, different hashes,
rebalanced prior components, and reproductions do not automatically earn credit.
Candidate-specific checks for additional recent work remain required. External
review is separate from the two local checker implementations.

## Timing and attribution

Preparation wall-clock time was not instrumented and is unavailable. `timing.json`
records only checkers’ instrumented internal verification times; process startup
and literature-review time are not folded into those values. There was no search
optimization during preparation. HILL transcription and derived certificate retain
credit to Yongchao Li, Yongzhuang Wei, Lang Li and Jian Guo, ToSC 2026, CC BY 4.0.
SBP artifact credit remains with Meltem Kurt Pehlivanoğlu and Mehmet Ali Demir;
see the upstream repository and existing THIRD-PARTY.md for original terms.
