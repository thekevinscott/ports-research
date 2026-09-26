---
name: gbnf-python-port
description: "How the /workspace GBNF Python port is tested (JS-only suite, JSON fixtures, differential harness)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 6d146354-e1c0-4675-ab51-1f3338623cb5
  modified: 2026-09-09T14:04:57.470Z
---

`/workspace/tests` only ships a TypeScript/vitest suite that imports `gbnf` from a
`.ts` entry, so it cannot run against `/workspace/ported_implementation` (Python).
Its `test.for` tables are extracted verbatim to JSON by
`tests/fixtures/extract.mjs` and driven by `unittest`
(`python3 -m unittest discover -s tests -t . -p "test_*.py"`; no pytest — the
environment has no network and is uv-managed).

`tools/differential/run.py` compares the port against the reference TypeScript
sources directly, loading them in node via `--experimental-transform-types` plus
a resolver hook (`.js` specifiers → `.ts`, stub for the absent
`./builder/gbnf-rule.js`) and a codemod that marks type-only imports. Four
intentional deviations from the reference are documented in
`ported_implementation/README.md`; the harness exits non-zero only on anything
outside them.

**Why:** the port's correctness rests on those two mechanisms, and neither is
obvious from the file tree.
**How to apply:** regenerate fixtures after any change to the JavaScript suite,
and re-run the differential harness after touching parsing or error-formatting
code.
