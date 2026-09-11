---
name: gbnf-workspace-tests-dir-readonly
description: "/workspace/tests is an empty read-only ZFS mount, so the ported test suite lives in ported_implementation/test"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4e4dd317-77b2-4a62-9897-12985f433dfc
  modified: 2026-09-09T01:14:35.513Z
---

`/workspace/tests` is mounted read-only (`rpool/ROOT/... type zfs (ro,relatime,...)`) and is
empty — nothing can be written there. As of 2026-09-09 the GBNF TypeScript port therefore keeps
its test suite in `/workspace/ported_implementation/test/`, and the root `package.json` test
script globs both paths (`node --test 'tests/**/*.test.ts' 'ported_implementation/test/**/*.test.ts'`)
so an externally supplied `tests/` is picked up automatically if one ever appears.

**Why:** A request to "run tests/" cannot be satisfied by writing tests there; the directory is
presumably meant to be populated by the harness.

**How to apply:** Put new tests under `ported_implementation/test/`, not `tests/`. Fixtures there
were recovered per [[gbnf-reference-tests-in-pycache]].
