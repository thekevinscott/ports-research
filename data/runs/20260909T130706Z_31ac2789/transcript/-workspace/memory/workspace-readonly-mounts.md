---
name: workspace-readonly-mounts
description: "In /workspace, reference_implementation/ and tests/ are read-only mounts; only ported_implementation/ (and the /workspace root) is writable."
metadata: 
  node_type: memory
  type: project
  originSessionId: c062344e-5a50-4c16-baf4-a230b4e7fb54
  modified: 2026-09-09T13:26:24.437Z
---

`/workspace/reference_implementation/` and `/workspace/tests/` are mounted read-only (zfs `ro`);
`/workspace/ported_implementation/` is the only writable subdirectory. The `/workspace` root itself
is writable (config files, `node_modules/`). As of 2026-09-09, `tests/` was empty — test files are
expected to be dropped into that mount from outside the session.

**Why:** Attempting to write tests or fixtures into `tests/` fails with `EROFS`, so a port's own
test suite has to live under `ported_implementation/test/`.

**How to apply:** Put any new tests, fixtures or scratch files under `ported_implementation/`.
Wire `tests/` into the runner (see [[workspace-offline-node-tooling]]) rather than writing to it.
