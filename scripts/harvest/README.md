# harvest

Builds `papers/`, the arXiv corpus behind the literature survey. The corpus itself is
gitignored — 741MB, and reproducible from these commands.

Was `harvest_citations.py` and `harvest_phase2.py` at the repo root.

## Use

`--papers` resolves against the working directory and defaults to `papers`, so run these
from the repo root.

```
uv run harvest citations   # phase 1: download papers cited by inline arXiv id
uv run harvest resolve     # phase 2A: title-resolve references that lack an inline id
uv run harvest convert     # phase 2B: convert harvested PDFs to markdown
uv run harvest phase2      # 2A then 2B
```

Every command hits the network and sleeps between requests to stay polite to arxiv:
0.5s per download in phase 1, 2.0s per API query in phase 2A. A full phase 2A pass over
54 seeds takes hours.

`resolve` accepts an arxiv API result only when the result's normalized title appears as a
substring of the normalized reference. That keeps false positives near zero no matter how
noisy the query is.

## Tests

```
just test-unit
```

Network-touching functions (`download`, `arxiv_query`) are not covered; the tests exercise
the parsing and corpus-scanning logic.
