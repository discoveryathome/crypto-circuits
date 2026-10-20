# Attribution and licenses

Original Python code and project documentation: MIT, see LICENSE.

The raw research artifacts retain their original licenses:

- `sources/nist/`: US NIST circuit collection; see its upstream README/license.
  Source comments identify the original construction authors and papers.
- `sources/jain/`: Swapnil Jain's October 2026 release. Code/circuits Apache-2.0;
  papers CC BY 4.0. Third-party CMT, Bernstein and other copied materials retain
  their individual terms. Source provenance is retained.
- `sources/circulant/`: Xu--Sun's circulant synthesis repository, GPLv3. Its
  circuit data and the four corresponding `--xu2026-*` normalized certificates
  retain that provenance/license; they are not relicensed under this pilot's MIT.
  No upstream C++ code was executed. A source file was read to inspect its format.
- `sources/linear2020.pdf` and `sources/linear2024.pdf`: the cited ToSC papers
  obtained from German National Library mirrors. Original author/license notices
  remain in the files.
- `sources/circulant2026.html` and `sources/mds2024.html`: original arXiv papers,
  with authors and license links intact.
- `sources/protocol/`: archived Discovery@Home v0 playbook/schema copied from
  the earlier local pilot; their upstream terms apply.

Converted certificates cite the raw construction source in `portfolio/*.json`.
The Tian constructions are explicit reproductions of published formulas, not
new pilot discoveries. The second checker and search algorithms are new,
independently written code; paper algorithms were not copied as executable code.

The project owner authorized this public release after the local experiment.
Keep this notice, source provenance, and upstream licenses with redistribution.
Historical LOCAL-only statements describe the experiment when it was run.
# Additional SBP artifacts

The data under `sources/sbp/` and derived `--sbp--` certificates reproduce work
by Meltem Kurt Pehlivanoğlu and Mehmet Ali Demir, PeerJ Computer Science
10:e1820 (2024), DOI 10.7717/peerj-cs.1820. Repository commit:
`f3880c8f87085e3eead3029593cee781e94ee60a`. The paper is CC BY 4.0.
The repository tree contains no explicit LICENSE file. Its raw data and
converted certificates are excluded from the public Git history and are not
relicensed under this pilot's MIT license. `sources/optional-artifacts.json`
records their source URLs, transformations and exact expected hashes.
`tools/fetch_optional_artifacts.py` retrieves source data directly from the
pinned upstream revision and regenerates the omitted certificates locally.
These local files stay ignored by Git. Publication of those artifacts would
require resolving their redistribution terms.
No upstream code or binaries from that repository were downloaded or run.

