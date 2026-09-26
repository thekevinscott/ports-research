---
name: workspace-offline-node-tooling
description: The /workspace box has no npm registry access and no tsc; vitest 2.1.3 is installed globally and must be symlinked into /workspace/node_modules to resolve.
metadata: 
  node_type: memory
  type: project
  originSessionId: c062344e-5a50-4c16-baf4-a230b4e7fb54
  modified: 2026-09-09T13:26:31.977Z
---

`npm install` fails with `E403 Filtered` for every package, so nothing can be added from the
registry. Node is v24. `vitest@2.1.3` is installed globally at
`/usr/local/lib/node_modules/vitest`, and `ln -s /usr/local/lib/node_modules/vitest
/workspace/node_modules/vitest` is what makes `import { defineConfig } from 'vitest/config'` and
`import { test } from 'vitest'` resolve from project files. There is no TypeScript compiler
anywhere on the box, so `tsc --noEmit` is not available — vitest/esbuild strips types without
checking them.

**Why:** Any plan that assumes installing dev dependencies (typescript, ts-node, jest) is dead on
arrival here.

**How to apply:** Write dependency-free TypeScript, use explicit `.ts` extensions in relative
imports (works with both vitest and `node --experimental-strip-types`), and verify behaviour with
tests rather than type checking. See [[workspace-readonly-mounts]] for where tests may live.
