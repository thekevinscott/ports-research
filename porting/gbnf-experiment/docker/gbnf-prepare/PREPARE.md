# The Preparation Step

This is how `gbnf` (the repo under test) gets prepared to be fed to an agent.

The image is built once per experimental condition. Three build args carry the
condition in: `SOURCE_LANGUAGE` (`python` or `typescript`),
`INCLUDE_PYTHON_TESTS` and `INCLUDE_TYPESCRIPT_TESTS` (`true` or `false`). Eight
combinations, eight images, eight tags. Everything up to `pnpm install` is
condition-independent and shared between them.

The whole of the output is `/reference`, and the host copies that folder out
whole. Kevin, 2026-09-26: "I want gbnf-experiment's container to copy all
relevant files to a specific folder - so that will be packages/{language} and
tests/{lang} - to /reference/source and reference/tests. /reference is the folder
that will be synced back." Nothing else lands there, and the host selects
nothing afterwards.

## 1. Clone

`gbnf` gets cloned at a pinned commit. The commit is old enough to be
pre-agentic-development. Kevin, 2026-09-26: "we clone and pin so that we have
reproducibility."

We use [thekevinscott/gbnf](https://github.com/thekevinscott/gbnf) at the SHA in
`gbnf_experiment.config`.

## 2. Patch

Out of the box, `gbnf` is missing some patches. For example, we need to apply
some Python code to generate the Python version of the integration test suite.

Kevin, 2026-09-26: "we apply patches because we don't want to modify the source
repo." What each one does, and the rule for adding one, is in
[patches/PATCHES.md](patches/PATCHES.md).

## 3. Build

`pnpm install`, then `pnpm --dir packages/test-writer build`.

## 4. Generate the flagged suites

The Dockerfile runs the test writer once per flagged language, into
`/reference/tests/<language>`. The suites are defined generically as markdown
under `packages/gbnf/test/`; the writer renders them per language. A language
whose flag is off is never generated.

Generation runs with the working directory inside `packages/gbnf/javascript`,
because the markdown cases resolve `../test/...` against it.

## 5. Assemble `/reference`

`/reference/source` is the source package, filtered on the way in;
`/reference/tests/<language>` is each flagged suite.

The filter is `rsync` with a per-language merge file in
[reference-filters/](reference-filters/), chosen over `git archive` with
`export-ignore` because `export-ignore` is a blacklist written into the repo's
own attributes, and this is a whitelist that belongs beside the Dockerfile. The
reasons for each exclusion are recorded in the rules files:

- colocated tests are withheld under every condition, so the held-out suite is
  the only one the agent can see;
- `dev/` is browser and node demo apps, not the library;
- `src/builder/` is a grammar-authoring DSL with no counterpart to port.

`tests/integration/fixtures/reference/` holds the expected listing for each of
the eight conditions, asserted file for file by
`tests/integration/reference_test.py`.
