# The Preparation Step

This is how `gbnf` (the repo under test) gets prepared to be fed to an agent.

The image is built once per experimental condition. The condition reaches it
as four build args: `SOURCE_LANGUAGE` (`python` or `javascript`, the upstream
package directory names), `SOURCE_RULES`, `TARGET_LANGUAGE` and
`TARGET_RULES`. The two rules args are whole rsync filter files, composed on
the host by `gbnf_experiment.prepare_filesystem.assemble_whitelist` from the
three flags, `include_unit_tests`, `include_source_integration_tests` and
`include_target_integration_tests`. Sixteen combinations. The image never
sees a flag. Everything through test generation is condition-independent and
shared between them.

The whole of the output is `/shared`, and the host copies that folder out
whole. Kevin, 2026-09-26: "/reference is the folder that will be synced back."
Nothing else lands there, and the host selects nothing afterwards. It holds:

- `/shared/source/<lang>`: the source package in its upstream layout,
  filtered on the way in. With `include_unit_tests` its colocated unit tests
  stay where they are; with `include_source_integration_tests` its generated
  suite stays where upstream wrote it.
- `/shared/target/<lang>`: the other language, present only with
  `include_target_integration_tests`. Its generated suite in upstream layout,
  plus the files upstream runs it with, and no source.

Tests come as upstream ships them, or not at all. Kevin, 2026-09-27: "It is not
feasible that for each repo we will 'fix' or otherwise patch a working test
environment, beyond the one that already ships with the repo. We may have 100s
of repos under test and therefore, the tests either work or they do not." So
there is no scaffolding of ours in `/shared`; whether a suite runs in the
sandbox is a fact about the repo. Unit tests are source-language only: the
other language's unit tests would hand the agent the module layout of the
implementation it is supposed to arrive at.

## 1. Clone

`gbnf` gets cloned at a pinned commit. The commit is old enough to be
pre-agentic-development. Kevin, 2026-09-26: "we clone and pin so that we have
reproducibility."

We use [thekevinscott/gbnf](https://github.com/thekevinscott/gbnf) at the SHA in
`gbnf_experiment.config`.

## 2. Patch

One patch, which drops two re-exports from the javascript index so the
filtered source typechecks. The python integration tests are generated as the
pin generates them, unpatched.

Kevin, 2026-09-26: "we apply patches because we don't want to modify the source
repo." What each one does, and the rule for adding one, is in
[patches/PATCHES.md](patches/PATCHES.md).

## 3. Build

`pnpm install`, then `pnpm --dir packages/test-writer build`, then
`pnpm install` again. pnpm skips a bin whose file is missing, and test-writer's
`write-tests` bin does not exist until it is built, so the first install never
linked it.

## 4. Generate both suites

Each language's suite is generated the way gbnf itself generates it, into the
place gbnf puts it:

- typescript: `pnpm --filter gbnf test:integration:write`, which writes
  `packages/gbnf/javascript/integration-tests/generated/`;
- python: `make write_integration_tests` in `packages/gbnf/python`, which writes
  `packages/gbnf/python/tests/generated/`.

Both run regardless of the condition, before the condition build args are
declared, so every condition shares those layers. Kevin, 2026-09-27: "Tests
write regardless of flags." The suites are defined once as markdown under
`packages/gbnf/test/`; test-writer renders them per language. The rules decide
only which suites the copies below let through.

At the pin the python Makefile names the suites it wants and skips
`grammars.md`, so python gets five suites where typescript gets six. That is
left as it is. Kevin, 2026-09-27: "I'd prefer that we build it up after we see
it in action. Let them fail. Let's see them fail, and let's fix them when they
fail and we can see how they fail."

## 5. Assemble `/shared/source/<lang>`

The source package, copied with `rsync` and the `SOURCE_RULES` build arg as
its filter. The rule files are in [reference-filters/<lang>/](reference-filters/):
`source.rules` is the whitelist and withholds tests; the host prepends
`unit-tests.rules` or `integration-tests.rules` for the flags that are on, and
since first match wins, their includes beat the exclusion. `rsync` was chosen
over `git archive` with `export-ignore` because `export-ignore` is a blacklist
written into the repo's own attributes, and this is a whitelist that belongs
beside the Dockerfile. The reasons for each exclusion are recorded in the
rules files:

- `dev/` is browser and node demo apps, not the library;
- `src/builder/` is a grammar-authoring DSL with no counterpart to port.

## 6. Assemble `/shared/target/<lang>`

Only when `TARGET_RULES` is non-empty: the same `rsync`, with that language's
`integration-tests.rules` and `harness.rules`. The harness rules name what
upstream runs the suite with (`package.json` and
`vitest.config.integration.ts`; `Makefile`, `pyproject.toml` and `uv.lock`) and
nothing else.

The composition is unit-tested for all sixteen conditions in
`assemble_whitelist_test.py`, against the real rule files.
