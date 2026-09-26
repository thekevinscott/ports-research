---
name: workspace-layout
description: /workspace port task — only ported_implementation/ is writable; tests/ and reference_implementation/ are read-only mounts; no npm network
metadata: 
  node_type: memory
  type: project
  originSessionId: 32b54802-6187-44f5-80a2-f6b0b85dcf77
  modified: 2026-09-09T18:47:03.207Z
---

In /workspace (GBNF Python→TypeScript port task), `reference_implementation/` and
`tests/` are read-only ZFS mounts and `tests/` is empty; only
`ported_implementation/` (and the /workspace root itself) is writable.

**Why:** "run tests/" cannot be satisfied as written — there is nothing there and
nothing can be added there. Graded tests are presumably mounted in later.

**How to apply:** Put your own tests under `ported_implementation/tests/` and run
`vitest run` from /workspace. There is no npm registry access and no `typescript`
package; `vitest` is installed globally at /usr/local/lib/node_modules and is
reachable via symlinks in /workspace/node_modules (`vitest`, plus `gbnf` →
ported_implementation so bare-specifier imports resolve). Vitest transpiles TS
with esbuild, so `tsc` type-checking is unavailable.
