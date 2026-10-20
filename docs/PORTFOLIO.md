# Fixed portfolio and reconciled evidence

Every tuple below is **AND / XOR / total gates / depth**. NOT is paid; constants and wiring are free. Complete coordinates come from checked certificates. Count-only claims remain separate. This is an audited artifact frontier, not a guarantee of exhaustive worldwide coverage.

The 59 initial witnesses and specifications were frozen before search. Later SBP imports and the direct ARIA derivation are separate prior guards; they cannot be counted as search discoveries. See [the literature audit](LITERATURE.md).

| Fixed instance | Profile / inputs | Frozen published witness tuples | Additional published XOR guard | Post-freeze checked prior tuples |
|---|---|---|---|---|
| [Aria](../portfolio/aria.json) | linear / 128 | 0/387/387/7 | — | 0/384/384/5 |
| [Fides+Midori+Mantis](../portfolio/fides-midori-mantis.json) | linear / 16 | 0/24/24/3 | — | 0/24/24/2 |
| [Joltik](../portfolio/joltik.json) | linear / 16 | 0/44/44/7 | 43 (depth unknown) | 0/47/47/4, 0/49/49/3 |
| [PrideL0](../portfolio/pridel0.json) | linear / 16 | 0/24/24/4 | — | 0/24/24/2 |
| [PrinceM0](../portfolio/princem0.json) | linear / 16 | 0/24/24/4 | — | 0/24/24/2 |
| [Qarma128](../portfolio/qarma128.json) | linear / 32 | 0/48/48/6 | — | — |
| [Qarma64](../portfolio/qarma64.json) | linear / 16 | 0/24/24/8 | — | 0/24/24/2 |
| [Skinny](../portfolio/skinny.json) | linear / 16 | 0/12/12/2 | — | 0/12/12/2 |
| [SmallScaleAES](../portfolio/smallscaleaes.json) | linear / 16 | 0/43/43/5 | 42 (depth unknown) | 0/47/47/4, 0/48/48/3 |
| [Anubis+ClefiaM0](../portfolio/anubis-clefiam0.json) | linear / 32 | 0/98/98/9 | 96 (depth unknown) | — |
| [ClefiaM1](../portfolio/clefiam1.json) | linear / 32 | 0/103/103/10 | — | — |
| [FoxMu4](../portfolio/foxmu4.json) | linear / 32 | 0/130/130/13 | — | — |
| [Square+AES+Mugi](../portfolio/square-aes-mugi.json) | linear / 32 | 0/88/88/5, 0/90/90/4, 0/92/92/6, 0/97/97/3 | — | — |
| [Twofish](../portfolio/twofish.json) | linear / 32 | 0/111/111/8 | 110 (depth unknown) | — |
| [WhirlwindM0](../portfolio/whirlwindm0.json) | linear / 32 | 0/159/159/14, 0/183/183/14, 0/200/200/16 | — | — |
| [WhirlwindM1](../portfolio/whirlwindm1.json) | linear / 32 | 0/169/169/11, 0/187/187/16, 0/241/241/18 | — | — |
| [FoxMu8](../portfolio/foxmu8.json) | linear / 64 | 0/540/540/14 | — | — |
| [Grostl](../portfolio/grostl.json) | linear / 64 | 0/410/410/12 | — | — |
| [Khazad](../portfolio/khazad.json) | linear / 64 | 0/366/366/18 | — | — |
| [Whirlpool+Maelstrom](../portfolio/whirlpool-maelstrom.json) | linear / 64 | 0/425/425/11 | — | — |
| [BKL16-4x4-GF16](../portfolio/bkl16-4x4-gf16.json) | linear / 16 | 0/41/41/5 | 40 (depth unknown) | 0/46/46/3 |
| [JPST17-4x4-GF16](../portfolio/jpst17-4x4-gf16.json) | linear / 16 | 0/40/40/6 | — | 0/43/43/4, 0/45/45/3 |
| [KLSW17-M-4x4-GF16](../portfolio/klsw17-m-4x4-gf16.json) | linear / 16 | 0/36/36/8 | — | — |
| [LS16-4x4-GF16](../portfolio/ls16-4x4-gf16.json) | linear / 16 | 0/44/44/4 | 43 (depth unknown) | 0/47/47/3 |
| [GF(2^4), modulus 0x13](../portfolio/gf4-13.json) | multiplier / 8 | 10/20/30/5 | — | — |
| [GF(2^5), modulus 0x25](../portfolio/gf5-25.json) | multiplier / 10 | 20/24/44/6 | — | — |
| [GF(2^6), modulus 0x49](../portfolio/gf6-49.json) | multiplier / 12 | 27/30/57/5 | — | — |
| [GF(2^7), modulus 0x89](../portfolio/gf7-89.json) | multiplier / 14 | 32/51/83/6, 32/51/83/7 | — | — |
| [GF(2^7), modulus 0x91](../portfolio/gf7-91.json) | multiplier / 14 | 32/55/87/11, 40/44/84/5 | — | — |
| [GF(2^8), modulus 0x11b](../portfolio/gf8-11b.json) | multiplier / 16 | 32/78/110/20, 33/76/109/18, 34/74/108/12, 34/74/108/19, 35/72/107/13, 35/72/107/19, 36/71/107/18, 36/74/110/7, 36/76/112/6, 43/69/112/14, 43/70/113/15, 43/71/114/9, 48/67/115/15, 48/69/117/6 | — | — |
| [4x4 block MDS on four 4-bit words](../portfolio/design-mds4x4-w4.json) | design / 16 | 0/35/35/6 | — | 0/38/38/5, 0/39/39/4, 0/40/40/4, 0/41/41/3, 0/43/43/3, 0/43/43/4, 0/45/45/3, 0/45/45/4, 0/46/46/3, 0/47/47/3, 0/47/47/4, 0/48/48/3, 0/48/48/4, 0/49/49/3 |
| [4x4 block MDS on four 4-bit words; involutory](../portfolio/design-mds4x4-w4-involution.json) | design / 16 | 0/36/36/7, 0/38/38/6, 0/41/41/6, 0/44/44/6, 0/44/44/8 | — | 0/38/38/5, 0/39/39/4, 0/40/40/4, 0/41/41/3, 0/43/43/3, 0/45/45/4, 0/47/47/4, 0/48/48/4, 0/49/49/3 |

The six multipliers have widths 4, 5, 6, 7, 7 and 8, with two distinct degree-7 moduli; GF256 uses the AES polynomial 0x11b. Polynomial coefficient order is least significant bit first. A free field isomorphism is not allowed. Full modulus and port details are in each JSON.

The two design problems fix four 4-bit words and branch number 5, with involution required in one. Arbitrary binary 4×4 blocks are allowed; the search sampled only a GF16 subfamily. Different matrices at the same coordinates do not count as progress. The GH1 and other SBP matrices are compared on those same design properties, not forced to equal a fixed map.

All source and witness paths, metrics, and unresolved claims are retained in [the machine-readable evidence table](../results/portfolio-frontier.json). Count minima across multiplier points must not be combined into a fictitious joint AND/XOR/depth optimum.
