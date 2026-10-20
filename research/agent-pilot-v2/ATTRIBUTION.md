# Sources and contributions

The fixed maps and starting constructions come from the publications and
artifact repositories recorded in `preparation/literature/comparators.json`
and the repository's `THIRD-PARTY.md`. New local rewrites do not erase that
provenance.

The Whirlwind candidates build on Buji Xu and Xiaoming Sun,
[Utilizing Circulant Structure to Optimize the Implementations of Linear
Layers](https://arxiv.org/html/2511.18226v2), May 2026 revision, and its
[released artifacts](https://github.com/DerryAlex/circulant_synth).
The paper is distributed under CC BY 4.0. This pilot converts in-place XOR
instructions to general straight-line programs, recomputes classical depth,
and changes the computation graphs through local search. The resulting
certificates are modified constructions, with exact lineage recorded in the
session and independent-review files. No improved quantum circuit or new
optimization theory is claimed.

AES starting circuits retain the author attribution and pinned paths supplied
by the [NIST circuit catalogue](https://csrc.nist.gov/projects/circuit-complexity/list-of-circuits).
Preparation additionally normalizes HILL's mixed-fanin Table 9 and a released
SBP AES circuit into binary XORs. Credit for HILL remains with Yongchao Li,
Yongzhuang Wei, Lang Li and Jian Guo, ToSC 2026; credit for SBP remains with
Meltem Kurt Pehlivanoğlu and Mehmet Ali Demir, 2024. Those conversions are
baseline reconciliation and receive no session discovery credit.

The initial search toolkit and session-specific methods were implemented
locally by the recorded agents. Published algorithm ideas retain their
literature attribution. No upstream optimizer was executed. Search authors,
baseline reconciliation, checker implementations and independent-agent
novelty review are separate recorded contributions. The review agent is
independent of each search author but belongs to the same model family.
External scientific review and any public authorship arrangements remain open.

This experiment is local. No author contact, remote submission, publication,
or donation intake occurred.
