# The Preparation Step

This is how `gbnf` (the repo under test) gets prepared to be fed to an agent.

The image is built once per experimental condition. The condition reaches it
as one build arg, `RULES`: a whole rsync filter file, composed on the host by
`gbnf_experiment.prepare_filesystem.assemble_whitelist` from the source
language and three flags, `include_unit_tests`,
`include_source_integration_tests` and `include_target_integration_tests`.
Sixteen combinations. The image never sees a flag or a language. Everything
through test generation is condition-independent and shared between them.

The whole of the output is `/shared`, and the host copies that folder out
whole. Kevin, 2026-09-26: "/reference is the folder that will be synced back."
Nothing else lands there, and the host selects nothing afterwards. It is
`packages/gbnf` in upstream layout, `python/` and `javascript/`, with only the
whitelisted files:

- the source language's package, with its colocated unit tests when
  `include_unit_tests`, and its generated integration suite when
  `include_source_integration_tests`, each where upstream keeps it;
- the other language's generated integration suite and the files upstream
  runs it with, no source, only when `include_target_integration_tests`.

Which language is source is not stated in the corpus. Kevin, 2026-09-28: "Do
_not_ call it source and target, instead call it javascript and python."

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

The python integration tests are generated as the pin generates them,
unpatched.

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

## 5. Assemble `/shared`

One `rsync` of `packages/gbnf/` with the `RULES` build arg as its filter. The
rule files are in `assemble_whitelist/reference-filters/<lang>/`, beside the
function that composes them, every pattern anchored to its language directory
so nothing matches across trees. `source.rules` is the whitelist and withholds
tests; the host puts `unit-tests.rules` or `integration-tests.rules` ahead of
it for the flags that are on, and since first match wins, their includes beat
the exclusion. `integration-tests.rules` also names the files upstream runs the suite with,
so the other language gets that file alone, or nothing, and a language with no
lines gets no files. The
composer closes with `+ */` and `- *` once. `rsync` was chosen over
`git archive` with `export-ignore` because `export-ignore` is a blacklist
written into the repo's own attributes, and this is a whitelist that belongs
to the experiment. The reasons for each exclusion are recorded in the rules
files:

- `dev/` is browser and node demo apps, not the library;
- `src/builder/` is a grammar-authoring DSL with no counterpart to port.

`assemble_whitelist_test.py` checks which rule files are composed, in what
order, for all sixteen conditions. `tests/integration/prepare_image_test.py`
builds this image for each of the sixteen conditions and asserts
`find /shared` equals `tests/integration/fixtures/shared/<condition>.txt`.
Those sixteen listings are what `/shared` holds per condition; the clone,
the patch, the generated suites, the rule files and the build-arg transport
are all under that one assertion. One clone and install; each further build
reruns only the copy layer.
