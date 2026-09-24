# The Preparation Step

This is how `gbnf` (the repo under test) gets prepared to be fed to an agent.

## 1. Clone

`gbnf` gets cloned at a pinned commit. The commit is old enough to be pre-agentic-development. 

We use [thekevinscott/gbnf](https://github.com/thekevinscott/gbnf) at the SHA in `gbnf_experiment.config`.

## 2. Patch

Out of the box, `gbnf` is missing some patches. For example, we need to apply some Python code to generate the Python version of the integration test suite.

Rather than push changes to the repo (which would make it harder to disambiguate agentic from non-agentic commits) we apply patches after clone.

What each one does, and the rule for adding one, is in [patches/PATCHES.md](patches/PATCHES.md).

## 3. Build

We run `pnpm install` and then we generate the integration tests on the fly. Integration tests are defined generically under `packages/gbnf/test/`.
