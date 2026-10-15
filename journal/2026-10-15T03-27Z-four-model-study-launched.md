# 2026-10-15T03:27Z — Prepared javascript tree patched; four-model study launched

Kevin on the two remaining vitest failures from the 03:20Z entry: "Like we're handing it broken code?" Both were slicing artefacts, not gbnf bugs: `javascript/tsconfig.json` extends `../../../tsconfig.json`, the monorepo root, which `/shared` does not carry; and `src/gbnf.test.ts` imports the withheld `src/builder/` for one test case. Kevin: "Continue excluding builder", "Can we take the root tsconfig and include in the other tsconfig?", "Cut the case. Smallest targeted edits".

Two prepare-time patches, same class as 0001: 0004 drops the `extends` and inlines the eight parent options; 0005 drops the one import and the one case. Prepare cache key moves (javascript, all suites: `d9464914dc2adf25`). Commit 3cc2947 on `sandbox-prompt`.

Probe (Sonnet 5.5, medium, vitest only, patched tree): first call from `/input` failed, vitest writes a temp config beside the config file and the mount is read-only; from a copy under `/tmp`, unit suite 24 files, 203 tests passed on the first run. Integration suite needed a build of the `gbnf` package; the esm vite config imports `vite-plugin-dts`, not installed, so the agent built from a copy without it; then 6 files, 773 tests passed.

Study launched 03:27Z: models claude-fable-5-1, claude-sonnet-5-5, claude-haiku-5-5, claude-opus-5-5; cells source-python and source-javascript with unit and source integration tests, effort medium; n=12, k=6, 96 runs; subscription auth; five_hour utilization 34 at launch, window resets 06:10Z. Log `internal/study_2026-10-14-models.log`. Usage watchdog every 30 minutes pauses at 97 and resumes after the reset.
