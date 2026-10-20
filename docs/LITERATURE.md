# Literature and baseline audit — 2026-10-20

This is an artifact-backed literature reconciliation, not a proof of exhaustive
worldwide coverage. In particular, complete classical size/depth frontiers for
all 24 linear maps were not recovered. That limitation blocks novelty claims;
it is never filled with an assumed depth or a weak benchmark.

## Sources consulted

| Source | Relevance and disposition |
|---|---|
| [NIST circuit catalogue](https://csrc.nist.gov/projects/circuit-complexity/list-of-circuits) and [pinned artifacts](https://github.com/usnistgov/Circuits/tree/8366158a4324ef902ce740f29ddc9f7ebb1018b2/data/slp) | Separate matrices and straight-line programs. Imported all selected published benchmarks. The catalogue explicitly does not promise current best-known status. |
| Xiang et al., [Optimizing Implementations of Linear Layers, ToSC 2020(2)](https://doi.org/10.13154/tosc.v2020.i2.120-145) | General and in-place XOR methods; paper archived as `sources/linear2020.pdf`. Several circuits are reproduced from NIST's attributed copies. |
| Yuan et al., [A Framework to Improve the Implementations of Linear Layers, ToSC 2024(2)](https://doi.org/10.46586/tosc.v2024.i2.322-347) | Table 2 compares g-XOR and s-XOR. Its count-only improvements remain guards where witnesses/depth are unavailable. The paper is archived from the German National Library. |
| Sun, Yang, Li, [Revisit the Boyar–Peralta Algorithm to Solve the Shortest Linear Program Problem, 2025/1493](https://eprint.iacr.org/2025/1493) | November 2025 revision reports 89 g-XOR AES MixColumns. NIST's verified August 2026 88-XOR circuit is stronger in count. Do not use the older 90/91 headlines as launch targets. |
| Xu and Sun, [Utilizing Circulant Structure to Optimize the Implementations of Linear Layers, May 2026 revision](https://arxiv.org/html/2511.18226v2) | Reproduced Whirlwind M0/M1 size and depth artifacts, converting CNOT updates to SSA and checking exact output wiring. The 159/169-XOR counts transfer; quantum depths do not. |
| [Xu--Sun artifact repository](https://github.com/DerryAlex/circulant_synth/tree/73ff05008ae1d9445a69bc792653726cdccdca5b) | Four normalized witnesses included. No C++ search code was compiled or run. |
| Huang et al., [GPU Acceleration for Boyar–Peralta Algorithm in High Dimensional Linear Layers, 2026/2520](https://eprint.iacr.asia/2026/2520) | October 17, 2026 preprint abstract reviewed through the archive mirror. Its reported Whirlwind 172/170 counts do not beat the verified 159/169 general-XOR upper bounds, even though they improve a narrower previous g-XOR table. GPU optimizer not reproduced. |
| Li, Wei, Li, Guo, [HILL, ToSC 2026(1), 506–526](https://doi.org/10.46586/tosc.v2026.i1.506-526) | Author publication list and paper abstract/text inspected. Uses mixed two/three-input XOR and hardware-area weights. Reported 79-operation/GE results are not 79 binary XORs. Numerical frontier not imported without normalization. Publisher robots restrictions prevent direct artifact retrieval in this session. |
| Jain, [Smaller Gate Counts for Polynomial-Basis Binary-Field Multipliers, October 2026](https://github.com/Swapnil-jain/gf2m-circuits/blob/9daf883e529ab4b9c80c66632683b403f0c69e89/papers/Jain_GF2m_multipliers_2026.pdf) | Reproduced all selected small-field witnesses and relevant historical CMT circuits. The paper itself disclaims systematic coverage. Its GF4/GF5 comparisons against naive reductions are not used as our benchmark: the released 30/44-gate circuits are. |
| Tian, Feng, Li, [On the construction of ultra-light MDS matrices, 2024](https://arxiv.org/html/2409.03298v1) | Reproduced 4-bit instantiations at 35 XORs and 36 XORs with involution. The first is Table 6 #17; the second is §3.5 tree 3 assignment 4 with shared scalar multiplication and the stated row order. Proved both with two implementations. |
| Wang et al., [Four by four MDS matrices with the fewest XOR gates based on words](https://doi.org/10.3934/amc.2021025) | Published 35-XOR general and 36-XOR involutory 4-bit constructions predate the pilot. Restricted word-model lower bounds are not global bit-circuit lower bounds. |
| [An STP-based model toward designing binary diffusion layers with the lowest latency, 2026](https://doi.org/10.1186/s42400-026-00617-z) | Exact small binary diffusion results show that broadening to small designs does not automatically create untouched problems. Its dimensions/branch-number tasks differ from our fixed block-MDS problems. |

## Reconciled count-only guards

The following stronger claims are retained even where their circuits were not
obtained. The stored point has **unknown depth**, not a fabricated full metric
tuple. They are upper bounds on attainable counts, never lower bounds.

| Instance | Imported lowest XOR count before trials | Additional published count guard |
|---|---:|---:|
| Joltik | 44 | 43 |
| SmallScaleAES | 43 | 42 |
| Anubis/Clefia M0 benchmark | 98 | 96 |
| Twofish | 111 | 110 |
| LS16 4x4 GF16 | 44 | 43 |
| BKL16 4x4 GF16 | 41 | 40, pending explicit matrix-identity confirmation |

These are taken from Yuan et al. Table 2, with corroboration in Xu--Sun Table 4
for overlapping rows. The CTG16 bibliography entry is Beierle, Kranz and Leander;
the alias alone is insufficient to establish a port-identical matrix, so that
last row stays guarded rather than certified.

Other selected rows retain their best retrieved witnesses with the exact source
path. No search result is called globally new merely because this audit did not
find a better circuit. The complete per-instance evidence is in
[PORTFOLIO.md](PORTFOLIO.md) and the specification JSON files.

## Post-search adjudication: ARIA

The frozen NIST ARIA artifact has 387 XORs and depth 7. An experimental candidate
at 386 XORs therefore appears to improve that file. Inspecting the published
artifact shows eight independent, identical bit planes, some with 48 gates and
others with 49. Copying its existing 48-gate bit-0 cone eight times gives
**384 XORs, depth 5**, verified by both implementations.

This is a direct consequence of an already published component, not credited
as a new trial discovery. It dominates the 386-gate proposal and illustrates why
catalogue wins are insufficient. The original frozen comparator is preserved;
the stronger derived-prior guard is a separate artifact under
`results/audit-baselines/`. Reproduce with `python3 tools/audit_aria.py`.
The 384 construction is not claimed to be the worldwide optimum or smallest
previously explicit ARIA publication.

## Open novelty work and meaningful next methods

A further post-freeze audit located Pehlivanoğlu and Demir's
[2024 SBP paper](https://doi.org/10.7717/peerj-cs.1820) and its
[released results](https://github.com/demirmehmet0/SBP/tree/f3880c8f87085e3eead3029593cee781e94ee60a).
Its two-input-XOR section already reports several of the apparent shallow
improvements, including Midori, PRINCE M0, PRIDE L0 and QARMA64 at 24 XORs,
depth 2. Its GH1 involutory design uses 41 XORs at depth 3. These are distinct
from its mixed-fan-in results. We imported the actual SBP witnesses as data,
matched their exact matrices or design properties, and checked them with both
implementations. The importer is `tools/audit_sbp.py`; results and any unmatched
files are in `results/audit-baselines/sbp-verification.json`.

These additional prior points do not change the frozen experiment. They
disqualify novelty claims in `results/novelty-audit.json` and update the
post-freeze literature guard table. Direct publisher retrieval returned 403
and PMC returned a browser challenge; indexed primary text and the author's
public artifact repository supplied the evidence. No challenge was bypassed.

Depth reductions from the imported corpus often come from ordinary sharing or
reassociation of circuits originally optimized for in-place execution. They may
be useful implementation variants, but their absence from our downloaded files
does not establish new literature results. Complete candidate-specific classical
depth-frontier audits remain necessary.

Potential methodological work includes cancellation-aware BP variants, structural
matrix decompositions, and bounded SAT replacement. Multiplier work should vary
bilinear decompositions, rather than only rewrite fixed products. These are
research directions, not promises of low-hanging records. The small seed-walk
pilot does not test those stronger methods.

AES S-box literature, including verified 28-AND circuits and Jain's 106 native
gate witnesses, remains in the separate AES pilot. It is an ambitious track,
not evidence for frequent routine discoveries.
